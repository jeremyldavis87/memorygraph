variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the services will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs"
  type        = list(string)
}

variable "ecs_cluster_id" {
  description = "ECS cluster ID"
  type        = string
}

variable "ecs_execution_role_arn" {
  description = "ECS execution role ARN"
  type        = string
}

variable "alb_security_group_id" {
  description = "ALB security group ID"
  type        = string
}

variable "redis_security_group_id" {
  description = "Redis security group ID"
  type        = string
}

variable "alb_listener_arn" {
  description = "ALB listener ARN"
  type        = string
}

variable "extractor_target_group_arn" {
  description = "Target group ARN for extractor service"
  type        = string
}

variable "inserter_target_group_arn" {
  description = "Target group ARN for inserter service"
  type        = string
}

variable "retriever_target_group_arn" {
  description = "Target group ARN for retriever service"
  type        = string
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}

# Resource specifications
variable "extractor_cpu" {
  description = "CPU units for extractor service"
  type        = number
  default     = 512
}

variable "extractor_memory" {
  description = "Memory for extractor service"
  type        = number
  default     = 1024
}

variable "extractor_desired_count" {
  description = "Desired count for extractor service"
  type        = number
  default     = 1
}

variable "inserter_cpu" {
  description = "CPU units for inserter service"
  type        = number
  default     = 256
}

variable "inserter_memory" {
  description = "Memory for inserter service"
  type        = number
  default     = 512
}

variable "inserter_desired_count" {
  description = "Desired count for inserter service"
  type        = number
  default     = 1
}

variable "retriever_cpu" {
  description = "CPU units for retriever service"
  type        = number
  default     = 256
}

variable "retriever_memory" {
  description = "Memory for retriever service"
  type        = number
  default     = 512
}

variable "retriever_desired_count" {
  description = "Desired count for retriever service"
  type        = number
  default     = 1
}
