# Secrets Manager Module
# Manages application secrets using AWS Secrets Manager

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (dev, prod)"
  type        = string
}

variable "braintrust_api_key" {
  description = "Braintrust API key"
  type        = string
  sensitive   = true
}

# Create secrets for the application
resource "aws_secretsmanager_secret" "app_secrets" {
  name        = "${var.project_name}-${var.environment}-secrets"
  description = "Application secrets for ${var.project_name} ${var.environment}"

  tags = {
    Project     = var.project_name
    Environment = var.environment
  }
}

# Store the secret values
resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    BRAINTRUST_API_KEY = var.braintrust_api_key
  })
}

# Output the secret ARN for use by ECS tasks
output "secrets_arn" {
  description = "ARN of the secrets manager secret"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "secrets_name" {
  description = "Name of the secrets manager secret"
  value       = aws_secretsmanager_secret.app_secrets.name
}
