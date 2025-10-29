# Graph Services Module
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ECR Repositories for Graph Services
resource "aws_ecr_repository" "extractor_service" {
  name                 = "${var.project_name}-${var.environment}-extractor-service"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-extractor-service"
    Environment = var.environment
    Project     = var.project_name
    Service     = "extractor"
  }
}

resource "aws_ecr_repository" "inserter_service" {
  name                 = "${var.project_name}-${var.environment}-inserter-service"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-inserter-service"
    Environment = var.environment
    Project     = var.project_name
    Service     = "inserter"
  }
}

resource "aws_ecr_repository" "retriever_service" {
  name                 = "${var.project_name}-${var.environment}-retriever-service"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-retriever-service"
    Environment = var.environment
    Project     = var.project_name
    Service     = "retriever"
  }
}

# Security Group for Graph Services
resource "aws_security_group" "graph_services" {
  name_prefix = "${var.project_name}-${var.environment}-graph-services-"
  vpc_id      = var.vpc_id

  # Allow inbound from ALB
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }

  # Allow outbound to Neo4j
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow outbound to OpenAI
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow outbound to Redis
  egress {
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [var.redis_security_group_id]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-graph-services"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Role for Graph Services
resource "aws_iam_role" "graph_services_task_role" {
  name = "${var.project_name}-${var.environment}-graph-services-task-role"

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
    Name        = "${var.project_name}-${var.environment}-graph-services-task-role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM Policy for Neo4j access
resource "aws_iam_policy" "neo4j_access_policy" {
  name        = "${var.project_name}-${var.environment}-neo4j-access-policy"
  description = "Policy for accessing Neo4j AuraDB"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:memorygraph/${var.environment}/neo4j-*"
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-neo4j-access-policy"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Attach Neo4j policy to task role
resource "aws_iam_role_policy_attachment" "graph_services_neo4j_policy" {
  role       = aws_iam_role.graph_services_task_role.name
  policy_arn = aws_iam_policy.neo4j_access_policy.arn
}

# CloudWatch Log Groups for Graph Services
resource "aws_cloudwatch_log_group" "extractor_service" {
  name              = "/ecs/${var.project_name}-${var.environment}-extractor-service"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-${var.environment}-extractor-service-logs"
    Environment = var.environment
    Project     = var.project_name
    Service     = "extractor"
  }
}

resource "aws_cloudwatch_log_group" "inserter_service" {
  name              = "/ecs/${var.project_name}-${var.environment}-inserter-service"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-${var.environment}-inserter-service-logs"
    Environment = var.environment
    Project     = var.project_name
    Service     = "inserter"
  }
}

resource "aws_cloudwatch_log_group" "retriever_service" {
  name              = "/ecs/${var.project_name}-${var.environment}-retriever-service"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-${var.environment}-retriever-service-logs"
    Environment = var.environment
    Project     = var.project_name
    Service     = "retriever"
  }
}

# ECS Task Definitions for Graph Services
resource "aws_ecs_task_definition" "extractor_service" {
  family                   = "${var.project_name}-${var.environment}-extractor-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.extractor_cpu
  memory                   = var.extractor_memory
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = aws_iam_role.graph_services_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "extractor-service"
      image = "${aws_ecr_repository.extractor_service.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "GRAPH_EXTRACTION_LLM_PROVIDER"
          value = "openai"
        },
        {
          name  = "GRAPH_EXTRACTION_MODEL"
          value = "gpt-5-nano"
        }
      ]

      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:memorygraph/${var.environment}/openai-api-key"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.extractor_service.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-extractor-service-task"
    Environment = var.environment
    Project     = var.project_name
    Service     = "extractor"
  }
}

resource "aws_ecs_task_definition" "inserter_service" {
  family                   = "${var.project_name}-${var.environment}-inserter-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.inserter_cpu
  memory                   = var.inserter_memory
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = aws_iam_role.graph_services_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "inserter-service"
      image = "${aws_ecr_repository.inserter_service.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "NEO4J_DATABASE"
          value = "neo4j"
        }
      ]

      secrets = [
        {
          name      = "NEO4J_URI"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:memorygraph/${var.environment}/neo4j-uri"
        },
        {
          name      = "NEO4J_USERNAME"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:memorygraph/${var.environment}/neo4j-username"
        },
        {
          name      = "NEO4J_PASSWORD"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:memorygraph/${var.environment}/neo4j-password"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.inserter_service.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-inserter-service-task"
    Environment = var.environment
    Project     = var.project_name
    Service     = "inserter"
  }
}

resource "aws_ecs_task_definition" "retriever_service" {
  family                   = "${var.project_name}-${var.environment}-retriever-service"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.retriever_cpu
  memory                   = var.retriever_memory
  execution_role_arn       = var.ecs_execution_role_arn
  task_role_arn            = aws_iam_role.graph_services_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "retriever-service"
      image = "${aws_ecr_repository.retriever_service.repository_url}:latest"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "NEO4J_DATABASE"
          value = "neo4j"
        }
      ]

      secrets = [
        {
          name      = "NEO4J_URI"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:memorygraph/${var.environment}/neo4j-uri"
        },
        {
          name      = "NEO4J_USERNAME"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:memorygraph/${var.environment}/neo4j-username"
        },
        {
          name      = "NEO4J_PASSWORD"
          valueFrom = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:memorygraph/${var.environment}/neo4j-password"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.retriever_service.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.environment}-retriever-service-task"
    Environment = var.environment
    Project     = var.project_name
    Service     = "retriever"
  }
}

# ECS Services for Graph Services
resource "aws_ecs_service" "extractor_service" {
  name            = "${var.project_name}-${var.environment}-extractor-service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.extractor_service.arn
  desired_count   = var.extractor_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.graph_services.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.extractor_target_group_arn
    container_name   = "extractor-service"
    container_port   = 8000
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name        = "${var.project_name}-${var.environment}-extractor-service"
    Environment = var.environment
    Project     = var.project_name
    Service     = "extractor"
  }
}

resource "aws_ecs_service" "inserter_service" {
  name            = "${var.project_name}-${var.environment}-inserter-service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.inserter_service.arn
  desired_count   = var.inserter_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.graph_services.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.inserter_target_group_arn
    container_name   = "inserter-service"
    container_port   = 8000
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name        = "${var.project_name}-${var.environment}-inserter-service"
    Environment = var.environment
    Project     = var.project_name
    Service     = "inserter"
  }
}

resource "aws_ecs_service" "retriever_service" {
  name            = "${var.project_name}-${var.environment}-retriever-service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.retriever_service.arn
  desired_count   = var.retriever_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.graph_services.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.retriever_target_group_arn
    container_name   = "retriever-service"
    container_port   = 8000
  }

  depends_on = [var.alb_listener_arn]

  tags = {
    Name        = "${var.project_name}-${var.environment}-retriever-service"
    Environment = var.environment
    Project     = var.project_name
    Service     = "retriever"
  }
}

# Data source for current AWS account ID
data "aws_caller_identity" "current" {}
