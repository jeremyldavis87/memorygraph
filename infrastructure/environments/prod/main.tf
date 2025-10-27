# Prod Environment Configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "memorygraph-terraform-state-prod"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# Local variables
locals {
  project_name = "memorygraph"
  environment  = "prod"
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name = local.project_name
  environment  = local.environment
  vpc_cidr     = "10.1.0.0/16"
  az_count     = 3
}

# Security Groups Module
module "security" {
  source = "../../modules/security"

  project_name = local.project_name
  environment  = local.environment
  vpc_id       = module.vpc.vpc_id
}

# Database Module
module "database" {
  source = "../../modules/database"

  project_name           = local.project_name
  environment            = local.environment
  private_subnet_ids     = module.vpc.private_subnet_ids
  rds_security_group_id  = module.security.rds_security_group_id
  redis_security_group_id = module.security.redis_security_group_id
  database_password      = var.database_password

  # Prod-specific settings
  instance_class         = "db.t3.small"
  allocated_storage      = 100
  max_allocated_storage  = 1000
  backup_retention_period = 30
  redis_node_type        = "cache.t3.small"
  redis_num_cache_nodes  = 2
}

# ECR Module
module "ecr" {
  source = "../../modules/ecr"

  project_name         = local.project_name
  environment          = local.environment
  image_retention_count = 20
}

# Load Balancer Module
module "alb" {
  source = "../../modules/alb"

  project_name          = local.project_name
  environment           = local.environment
  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  alb_security_group_id = module.security.alb_security_group_id
}

# ECS Module
module "ecs" {
  source = "../../modules/ecs"

  project_name                = local.project_name
  environment                 = local.environment
  aws_region                  = var.aws_region
  private_subnet_ids          = module.vpc.private_subnet_ids
  ecs_tasks_security_group_id = module.security.ecs_tasks_security_group_id
  target_group_arn            = module.alb.target_group_arn
  alb_listener_arn            = module.alb.listener_arn
  backend_ecr_repository_url  = module.ecr.backend_ecr_repository_url
  database_endpoint           = module.database.rds_endpoint
  database_username           = "memorygraph"
  database_password           = var.database_password
  redis_endpoint              = module.database.redis_endpoint

  # Prod-specific settings
  task_cpu         = "1024"
  task_memory      = "2048"
  desired_count    = 3
  log_retention_days = 30
}

# Secrets Manager Module
module "secrets_manager" {
  source = "../../modules/secrets-manager"

  project_name         = local.project_name
  environment          = local.environment
  braintrust_api_key   = var.braintrust_api_key
}