# modules/database/variables.tf

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for database"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "Security group ID of ECS tasks"
  type        = string
}

variable "sns_topic_arn" {
  description = "SNS Topic ARN for alerting"
  type        = string
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "14.9"
}

variable "instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "replica_instance_class" {
  description = "RDS replica instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GiB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum allocated storage in GiB for autoscaling"
  type        = number
  default     = 100
}

variable "backup_retention_days" {
  description = "Backup retention days by environment"
  type        = map(number)
  default     = {
    development = 1
    staging     = 7
    production  = 30
  }
}

variable "deletion_protection" {
  description = "Enable deletion protection"
  type        = bool
  default     = true
}

# Add outputs for the database module
output "endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "secret_arn" {
  description = "ARN of the database credentials secret"
  value       = aws_secretsmanager_secret.rds.arn
}

output "security_group_id" {
  description = "Security group ID of the database"
  value       = aws_security_group.database.id
}

output "replica_endpoint" {
  description = "Database replica endpoint"
  value       = var.environment == "production" ? aws_db_instance.replica[0].endpoint : null
}