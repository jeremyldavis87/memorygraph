variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "memorygraph"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Note: OpenAI API key and JWT secret are now stored in AWS Secrets Manager
# They are retrieved at runtime by the ECS tasks

variable "allowed_origins" {
  description = "Allowed CORS origins"
  type        = list(string)
  default     = ["http://localhost:3000", "http://localhost:3001"]
}