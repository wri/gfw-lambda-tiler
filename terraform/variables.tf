variable "environment" { type = string }
variable "log_level" { type = string }
variable "log_retention" {
  default     = 30
  type        = number
  description = "Time in days to keep logs."
}