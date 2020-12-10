resource "aws_cloudwatch_log_group" "default" {
  name              = "/aws/lambda/us-east-1.${local.project}${local.name_suffix}"
  retention_in_days = var.log_retention
}