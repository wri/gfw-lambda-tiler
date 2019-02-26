"""
"""
import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_dir)

import utils

from lambda_proxy.proxy import API


APP = API(app_name="lambda-tiler")


@APP.route('/tiles/<int:z>/<int:x>/<int:y>.png', methods=['GET'], cors=True)
def tile(tile_z, tile_x, tile_y):
    """
    Handle tile requests
    """
    address = 's3://gfw2-data/forest_change/umd_landsat_alerts/prod/rgb/z_{}.vrt'.format(tile_z)

    # read directly from the VRT --> numpy array
    tile = utils.tile(address, tile_x, tile_y, tile_z)

    # write out 3 band RGB PNG
    png = utils.array_to_img(tile)

    return ('OK', 'image/png', png)


@APP.route('/favicon.ico', methods=['GET'], cors=True)
def favicon():
    """
    favicon
    """
    return('NOK', 'text/plain', '')
