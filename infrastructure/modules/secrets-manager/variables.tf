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
