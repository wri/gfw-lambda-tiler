# glad-lambda-tiler
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/3f7d55d037bb4b738f50c98d672e440b)](https://www.codacy.com/gh/wri/gfw-lambda-tiler/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=wri/gfw-lambda-tiler&amp;utm_campaign=Badge_Grade)
This builds a lambda endpoint that accepts a Z/X/Y tile ID and returns a map tile PNG.
It uses rasterio to perform a windowed read against any WM Tileset in GFW Data Lake

