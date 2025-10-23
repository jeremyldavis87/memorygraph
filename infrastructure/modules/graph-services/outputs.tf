output "extractor_ecr_repository_url" {
  description = "ECR repository URL for extractor service"
  value       = aws_ecr_repository.extractor_service.repository_url
}

output "inserter_ecr_repository_url" {
  description = "ECR repository URL for inserter service"
  value       = aws_ecr_repository.inserter_service.repository_url
}

output "retriever_ecr_repository_url" {
  description = "ECR repository URL for retriever service"
  value       = aws_ecr_repository.retriever_service.repository_url
}

output "graph_services_security_group_id" {
  description = "Security group ID for graph services"
  value       = aws_security_group.graph_services.id
}

output "extractor_service_name" {
  description = "ECS service name for extractor service"
  value       = aws_ecs_service.extractor_service.name
}

output "inserter_service_name" {
  description = "ECS service name for inserter service"
  value       = aws_ecs_service.inserter_service.name
}

output "retriever_service_name" {
  description = "ECS service name for retriever service"
  value       = aws_ecs_service.retriever_service.name
}

output "extractor_task_definition_arn" {
  description = "Task definition ARN for extractor service"
  value       = aws_ecs_task_definition.extractor_service.arn
}

output "inserter_task_definition_arn" {
  description = "Task definition ARN for inserter service"
  value       = aws_ecs_task_definition.inserter_service.arn
}

output "retriever_task_definition_arn" {
  description = "Task definition ARN for retriever service"
  value       = aws_ecs_task_definition.retriever_service.arn
}
