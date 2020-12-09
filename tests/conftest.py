import os

import numpy as np
import rasterio
from rasterio.enums import ColorInterp
from rasterio.windows import Window

##################
# Create Test data
##################


profile = {"driver": "GTiff", "height": 512, "width": 512, "count": 4, "dtype": "uint8"}

bands = range(1, 5)
windows = ((0, 0), (0, 256), (256, 0), (256, 256))

fixtures = os.path.join(os.path.dirname(__file__), "fixtures")
TEST_FILE = os.path.join(fixtures, "test.tif")

with rasterio.open(TEST_FILE, "w", **profile) as dst:
    for band in bands:
        for i, window in enumerate(windows):
            data = np.ones(shape=(256, 256), dtype="uint8") * i
            dst.write(data, window=Window(window[0], window[1], 256, 256), indexes=band)
    dst.colorinterp = [
        ColorInterp.red,
        ColorInterp.green,
        ColorInterp.blue,
        ColorInterp.alpha,
    ]
