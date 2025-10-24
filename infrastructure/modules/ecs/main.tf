# ECS Module
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-cluster"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "main" {
  family                   = "${var.project_name}-${var.environment}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${var.backend_ecr_repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.database_username}:${var.database_password}@${var.database_endpoint}/memorygraph"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${var.redis_endpoint}:6379/0"
        },
        {
          name  = "API_V1_STR"
          value = "/api/v1"
        },
        {
          name  = "ALGORITHM"
          value = "HS256"
        },
        {
          name  = "ACCESS_TOKEN_EXPIRE_MINUTES"
          value = "30"
        },
        {
          name  = "DEBUG"
          value = var.environment == "dev" ? "true" : "false"
        },
        {
          name  = "LOG_LEVEL"
          value = var.environment == "dev" ? "DEBUG" : "INFO"
        },
        {
          name  = "ENVIRONMENT"
          value = var.environment
        }
      ]

      secrets = [
        {
          name      = "SECRET_KEY"
          valueFrom = data.aws_secretsmanager_secret.jwt_secret.arn
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = data.aws_secretsmanager_secret.openai_api_key.arn
        },
        {
          name      = "ANTHROPIC_API_KEY"
          valueFrom = data.aws_secretsmanager_secret.anthropic_api_key.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.main.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-task"
    Environment = var.environment
    Project     = var.project_name
  }
}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = "${var.project_name}-${var.environment}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_tasks_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "backend"
    container_port   = 8000
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name        = "${var.project_name}-${var.environment}-service"
    Environment = var.environment
    Project     = var.project_name
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "main" {
  name              = "/ecs/${var.project_name}-${var.environment}"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-${var.environment}-logs"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Role for ECS Execution
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.project_name}-${var.environment}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-ecs-execution-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM Role for ECS Tasks
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-ecs-task-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Policy for Secrets Manager access
resource "aws_iam_policy" "secrets_manager_policy" {
  name        = "${var.project_name}-${var.environment}-secrets-manager-policy"
  description = "Policy for accessing Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          data.aws_secretsmanager_secret.jwt_secret.arn,
          data.aws_secretsmanager_secret.openai_api_key.arn,
          data.aws_secretsmanager_secret.anthropic_api_key.arn
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-secrets-manager-policy"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach the secrets manager policy to the ECS execution role
resource "aws_iam_role_policy_attachment" "ecs_execution_secrets_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.secrets_manager_policy.arn
}

# Data source for current AWS account ID
data "aws_caller_identity" "current" {}

# Data sources for Secrets Manager secrets
data "aws_secretsmanager_secret" "jwt_secret" {
  name = "memorygraph/jwt-secret"
}

data "aws_secretsmanager_secret" "openai_api_key" {
  name = "memorygraph/openai-api-key"
}

data "aws_secretsmanager_secret" "anthropic_api_key" {
  name = "memorygraph/anthropic-api-key"
}