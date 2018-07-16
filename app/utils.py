import base64
import logging
from io import BytesIO

import numpy as np

import mercantile

import rasterio
from rasterio.enums import Resampling

from PIL import Image


logger = logging.getLogger(__name__)


def array_to_img(arr):
    """Convert an array to an base64 encoded img

    Attributes
    ----------
    arr : numpy ndarray
        Image array to encode.

    Returns
    -------
    out : str
        base64 encoded PNG image.
    """

    img = Image.fromarray(arr, mode='RGB')

    sio = BytesIO()
    params = {'compress_level': 0}

    img.save(sio, 'png', **params)
    sio.seek(0)

    return base64.b64encode(sio.getvalue()).decode()


def tile(address, tile_x, tile_y, tile_z):
    """Create mercator tile from any images.

    Attributes
    ----------

    address : str
        file url.
    tile_x : int
        Mercator tile X index.
    tile_y : int
        Mercator tile Y index.
    tile_z : int
        Mercator tile ZOOM level.

    Returns
    -------
    data : numpy ndarray
    """

    mercator_tile = mercantile.Tile(x=tile_x, y=tile_y, z=tile_z)
    w, s, e, n = mercantile.xy_bounds(mercator_tile)

    tilesize = 256
    indexes = (1,2,3)

    out_shape = (len(indexes), tilesize, tilesize)

    with rasterio.open(address) as src:

        window = src.window(w, s, e, n, precision=21)

        data = src.read(window=window, boundless=True, out_shape=out_shape, indexes=indexes)

    # moves data from (3, 256, 256) format to (256, 256, 3)
    # PIL will read it in both ways, but for some reason
    # only propogates the first band to the other three 
    # when in (3, 256, 256)
    data = np.dstack((data[0], data[1], data[2]))

    return data

