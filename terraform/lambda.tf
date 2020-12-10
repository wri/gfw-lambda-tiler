
data "archive_file" "default" {
  type        = "zip"
  source_dir  = "${path.root}/../app"
  output_path = "${path.root}/archive/app.zip"
}


resource "aws_lambda_function" "default" {
  # Function was imported from core module and we need first to detach it from cloud front, wait until all replicas are deleted and then rename it

  function_name    = "${local.project}${local.name_suffix}"
  filename         = data.archive_file.default.output_path
  source_code_hash = data.archive_file.default.output_base64sha256
  role             = aws_iam_role.default.arn
  layers = [data.terraform_remote_state.lambda_layers.outputs.py38_pillow_801_arn,
  data.terraform_remote_state.lambda_layers.outputs.py38_rasterio_118_arn]
  runtime     = "python3.8"
  handler     = "lambda_function.handler"
  memory_size = 128
  timeout     = 3
  publish     = true
  tags        = local.tags
  environment {
    variables = {
      LOG_LEVEL = var.log_level
    }
  }
}
