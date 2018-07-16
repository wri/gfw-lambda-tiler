"""
"""
import sys
import os

app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_dir)

import main
from utils import array_to_img

from lambda_proxy.proxy import API


APP = API(app_name="lambda-tiler")


@APP.route('/tiles/<int:z>/<int:x>/<int:y>.png', methods=['GET'], cors=True)
def tile(tile_z, tile_x, tile_y):
    """
    Handle tile requests
    """
    address = 's3://palm-risk-poc/data/glad/rgb/z_{}.vrt'.format(tile_z)

    tile, mask = main.tile(address, tile_x, tile_y, tile_z, None)

    # remove unused alpha band
    tile = tile[0:3]

    tile = array_to_img(tile, 'png', mask=None)

    return ('OK', 'image/png', tile)


@APP.route('/favicon.ico', methods=['GET'], cors=True)
def favicon():
    """
    favicon
    """
    return('NOK', 'text/plain', '')
