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

variable "certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS (optional)"
  type        = string
  default     = ""
}

variable "domain_name" {
  description = "Domain name for the ALB (optional)"
  type        = string
  default     = ""
}

variable "braintrust_api_key" {
  description = "Braintrust API key"
  type        = string
  sensitive   = true
}