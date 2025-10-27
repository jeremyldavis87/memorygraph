variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "braintrust_api_key" {
  description = "Braintrust API key"
  type        = string
  sensitive   = true
}