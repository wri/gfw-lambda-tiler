import os
import re
import base64
import logging
import datetime
from io import BytesIO

import numpy as np
import numexpr as ne

import mercantile

import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.plot import reshape_as_image
from rio_toa import reflectance, brightness_temp, toa_utils

from rio_tiler.errors import (RioTilerError,
                              InvalidFormat,
                              InvalidLandsatSceneId,
                              InvalidSentinelSceneId,
                              InvalidCBERSSceneId)

from PIL import Image

# Python 2/3
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen


logger = logging.getLogger(__name__)


def tile_exists(bounds, tile_z, tile_x, tile_y):
    """Check if a mercatile tile is inside a given bounds

    Attributes
    ----------

    bounds : list
        WGS84 bounds (left, bottom, right, top).
    x : int
        Mercator tile Y index.
    y : int
        Mercator tile Y index.
    z : int
        Mercator tile ZOOM level.

    Returns
    -------
    out : boolean
        if True, the z-x-y mercator tile in inside the bounds.
    """

    mintile = mercantile.tile(bounds[0], bounds[3], tile_z)
    maxtile = mercantile.tile(bounds[2], bounds[1], tile_z)

    return (tile_x <= maxtile.x + 1) \
        and (tile_x >= mintile.x) \
        and (tile_y <= maxtile.y + 1) \
        and (tile_y >= mintile.y)


def array_to_img(arr, tileformat='png', mask=None, color_map=None):
    """Convert an array to an base64 encoded img

    Attributes
    ----------
    arr : numpy ndarray
        Image array to encode.
    tileformat : str (default: png)
        Image format to return (Accepted: "jpg" or "png")
    Mask: numpy ndarray
        Mask
    color_map: numpy array
        ColorMap array (see: utils.get_colormap)

    Returns
    -------
    out : str
        base64 encoded PNG or JPEG image.
    """

    if tileformat not in ['png', 'jpg']:
        raise InvalidFormat('Invalid {} extension'.format(tileformat))

    if arr.dtype != np.uint8:
        logger.error('Data casted to UINT8')
        arr = arr.astype(np.uint8)

    if len(arr.shape) >= 3:
        arr = reshape_as_image(arr)
        arr = arr.squeeze()

    if len(arr.shape) != 2 and color_map:
        raise InvalidFormat('Cannot apply colormap on a multiband image')

    if len(arr.shape) == 2:
        mode = 'L'
    else:
        mode = 'RGB'

    img = Image.fromarray(arr, mode=mode)
    if color_map:
        img.putpalette(color_map)

    sio = BytesIO()
    if tileformat == 'jpg':
        tileformat = 'jpeg'
        params = {'subsampling': 0, 'quality': 100}
    else:
        if mask is not None:
            mask_img = Image.fromarray(mask.astype(np.uint8))
            img.putalpha(mask_img)
        params = {'compress_level': 0}

    img.save(sio, tileformat, **params)
    sio.seek(0)

    return base64.b64encode(sio.getvalue()).decode()


def tile_band_worker(address, bounds, tilesize, indexes=[1], nodata=None, alpha=None):
    """Read band data

    Attributes
    ----------

    address : file address
    bounds : Mercator tile bounds to retrieve
    tilesize : Output image size
    indexes : list of ints or a single int, optional, (default: 1)
        If `indexes` is a list, the result is a 3D array, but is
        a 2D array if it is a band index number.
    nodata: int or float, optional (defaults: None)
    alpha: int, optional (defaults: None)
        Force alphaband if not present in the dataset metadata

    Returns
    -------
    out : array, int
        returns pixel value.
    """
    w, s, e, n = bounds

    if alpha is not None and nodata is not None:
        raise RioTilerError('cannot pass alpha and nodata option')

    if isinstance(indexes, int):
        indexes = [indexes]

    out_shape = (len(indexes), tilesize, tilesize)

    with rasterio.open(address) as src:
        with WarpedVRT(src, dst_crs='EPSG:3857', resampling=Resampling.nearest,
                       src_nodata=nodata, dst_nodata=nodata) as vrt:

                            window = vrt.window(w, s, e, n, precision=21)

                            data = vrt.read(window=window,
                                            boundless=True,
                                            resampling=Resampling.nearest,
                                            out_shape=out_shape,
                                            indexes=indexes)

                            if nodata is not None:
                                mask = np.all(data != nodata, axis=0).astype(np.uint8) * 255
                            elif alpha is not None:
                                mask = vrt.read(alpha, window=window,
                                                out_shape=(tilesize, tilesize),
                                                boundless=True,
                                                resampling=Resampling.nearest)
                            else:
                                mask = vrt.read_masks(1, window=window,
                                                      out_shape=(tilesize, tilesize),
                                                      boundless=True,
                                                      resampling=Resampling.nearest)

    return data, mask

