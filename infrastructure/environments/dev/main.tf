# Dev Environment Configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "memorygraph-terraform-state-dev"
    key    = "dev/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# Local variables
locals {
  project_name = "memorygraph"
  environment  = "dev"
}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name = local.project_name
  environment  = local.environment
  vpc_cidr     = "10.0.0.0/16"
  az_count     = 2
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

  # Dev-specific settings
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  max_allocated_storage  = 50
  backup_retention_period = 3
  redis_node_type        = "cache.t3.micro"
  redis_num_cache_nodes  = 1
}

# ECR Module
module "ecr" {
  source = "../../modules/ecr"

  project_name         = local.project_name
  environment          = local.environment
  image_retention_count = 5
}

# Load Balancer Module
module "alb" {
  source = "../../modules/alb"

  project_name          = local.project_name
  environment           = local.environment
  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  alb_security_group_id = module.security.alb_security_group_id
  certificate_arn       = var.certificate_arn
  domain_name           = var.domain_name
}

# ECS Module
module "ecs" {
  source = "../../modules/ecs"

  project_name                = local.project_name
  environment                 = local.environment
  aws_region                  = var.aws_region
  private_subnet_ids          = module.vpc.private_subnet_ids
  public_subnet_ids           = module.vpc.public_subnet_ids
  ecs_tasks_security_group_id = module.security.ecs_tasks_security_group_id
  target_group_arn            = module.alb.backend_target_group_arn
  alb_listener_arn            = module.alb.listener_arn
  backend_ecr_repository_url  = module.ecr.backend_ecr_repository_url
  frontend_ecr_repository_url = module.ecr.frontend_ecr_repository_url
  frontend_target_group_arn   = module.alb.frontend_target_group_arn
  database_endpoint           = module.database.rds_endpoint
  database_username           = "memorygraph"
  database_password           = var.database_password
  redis_endpoint              = module.database.redis_endpoint

  # Dev-specific settings
  task_cpu         = "256"
  task_memory      = "512"
  desired_count    = 1
  frontend_task_cpu    = "256"
  frontend_task_memory = "512"
  frontend_desired_count = 1
  log_retention_days = 3
}


# Secrets Manager Module
module "secrets_manager" {
  source = "../../modules/secrets-manager"

  project_name         = local.project_name
  environment          = local.environment
  braintrust_api_key   = var.braintrust_api_key
}

# Graph Services Module
module "graph_services" {
  source = "../../modules/graph-services"

  project_name                = local.project_name
  environment                 = local.environment
  aws_region                  = var.aws_region
  vpc_id                      = module.vpc.vpc_id
  private_subnet_ids          = module.vpc.private_subnet_ids
  ecs_cluster_id              = module.ecs.cluster_id
  ecs_execution_role_arn      = module.ecs.execution_role_arn
  alb_security_group_id       = module.security.alb_security_group_id
  redis_security_group_id     = module.security.redis_security_group_id
  alb_listener_arn            = module.alb.listener_arn

  # Dev-specific settings
  extractor_cpu              = "256"
  extractor_memory           = "512"
  extractor_desired_count    = 0  # Disabled for dev
  inserter_cpu               = "256"
  inserter_memory            = "512"
  inserter_desired_count     = 0  # Disabled for dev
  retriever_cpu              = "256"
  retriever_memory           = "512"
  retriever_desired_count    = 0  # Disabled for dev
  log_retention_days         = 3

  # Target groups (using main ALB target group for now)
  extractor_target_group_arn = module.alb.target_group_arn
  inserter_target_group_arn  = module.alb.target_group_arn
  retriever_target_group_arn = module.alb.target_group_arn
}