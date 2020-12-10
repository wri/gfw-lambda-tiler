# glad-lambda-tiler
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/3f7d55d037bb4b738f50c98d672e440b)](https://www.codacy.com/gh/wri/gfw-lambda-tiler/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=wri/gfw-lambda-tiler&amp;utm_campaign=Badge_Grade)
This builds a lambda endpoint that accepts a Z/X/Y tile ID and returns a map tile PNG.
It uses rasterio to perform a windowed read against VRTs of the GLAD data, which currently live here:

s3://palm-risk-poc/data/glad/rgb/

### Deployment

- Build the package: `make all`
- install serverless: `npm install`
- deploy to our endpoint: `sls deploy`

### Example PNG response
https://tiles.globalforestwatch.org/glad_prod/tiles/12/1428/2167.png

### Cloudfront / S3 / WRI DNS magic
So how does this all happen? Let's work backwards:

1. tiles.globalforestwatch.org/ is an alias for the cloudfront distribution d178s5l0vmo3yy.cloudfront.net
2. This cloudfront distrbution caches requests made to wri-tiles.s3-website-us-east-1.amazonaws.com
3. This URL is the static website endpoint for the S3 bucket s3://wri-tiles/

### Now the fun part!
We pre-generate tiles for zooms 0 - 8 here: s3://wri-tiles/glad_prod/tiles/. So when requests are made to tiles.globalforestwatch.org/glad_prod/tiles for those zooms, it responds with the saved PNG.

This pre-generation work is done by the [mapnik-forest-change-tiles repo](https://github.com/wri/mapnik-forest-change-tiles/). It's pretty quick to generate zooms 0 - 8 (20 minutes on a large machine), and it's cost effective to serve static images for tiles that are likely to be viewed.

If the PNG *doesn't* exist in S3 (i.e. is a tile at zooms 9 - 12), we have a special 404 redirect that pushes this request to the lambda function in this repo. This URL rewrite rule is documented in this repo as `s3_redirect.xml`. The rewrite rule grabs the required params (z / x / y) and then passes them along to our lambda endpoint like so:
https://8nfgezzlb1.execute-api.us-east-1.amazonaws.com/dev/tiles/12/1428/2167.png

**If you need to edit this rewrite rule, go to the AWS Console --> S3 --> wri-tiles bucket --> Properties --> static website hosting --> redirection rules.**

### That's all folks

It may seem complicated (and it is) but unfortunately this convoluted system was necessary given the requirements (unchanging tile URL, storage on S3, HTTPS access, etc). Hopefully this doc serves as a good starting point to understand the system!


