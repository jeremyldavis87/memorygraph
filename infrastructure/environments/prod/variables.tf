variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}