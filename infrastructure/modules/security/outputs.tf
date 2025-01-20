output "kms_key_arn" {
  description = "ARN of the main KMS key"
  value       = aws_kms_key.main.arn
}

output "cloudwatch_kms_key_arn" {
  description = "ARN of the CloudWatch KMS key"
  value       = aws_kms_key.cloudwatch.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the ECS task role"
  value       = aws_iam_role.ecs_task_role.arn
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.ecs_task_execution_role.arn
}

output "ssm_parameter_prefix" {
  description = "Prefix for SSM parameters"
  value       = "/${var.environment}/${var.app_name}"
}