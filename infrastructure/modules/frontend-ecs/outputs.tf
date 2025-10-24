output "frontend_service_name" {
  description = "Name of the frontend ECS service"
  value       = aws_ecs_service.frontend.name
}

output "frontend_task_definition_arn" {
  description = "ARN of the frontend ECS task definition"
  value       = aws_ecs_task_definition.frontend.arn
}

output "frontend_task_definition_family" {
  description = "Family of the frontend ECS task definition"
  value       = aws_ecs_task_definition.frontend.family
}
