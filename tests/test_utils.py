from rasterio.windows import Window

from app.utils import tile
from tests.conftest import TEST_FILE


def test_tile():

    data = tile(TEST_FILE, Window(0, 0, 256, 256))
    assert data.shape == (256, 256, 4)
