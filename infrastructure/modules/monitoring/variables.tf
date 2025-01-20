# modules/monitoring/variables.tf

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

variable "private_subnet_ids" {
  description = "Private subnet IDs"
  type        = list(string)
}

variable "ecs_cluster_name" {
  description = "ECS cluster name"
  type        = string
}

variable "ecs_service_name" {
  description = "ECS service name"
  type        = string
}

variable "alb_arn_suffix" {
  description = "ALB ARN suffix"
  type        = string
}

variable "db_instance_identifier" {
  description = "RDS instance identifier"
  type        = string
}

variable "cloudwatch_kms_key_arn" {
  description = "KMS key ARN for CloudWatch encryption"
  type        = string
}

variable "sns_kms_key_arn" {
  description = "KMS key ARN for SNS encryption"
  type        = string
}

variable "alert_email_addresses" {
  description = "List of email addresses for alerts"
  type        = list(string)
}

variable "app_url" {
  description = "Application URL for synthetic monitoring"
  type        = string
}

variable "monitoring_bucket" {
  description = "S3 bucket for monitoring artifacts"
  type        = string
}

variable "log_retention_days" {
  description = "Log retention days by environment"
  type        = map(number)
  default = {
    development = 7
    staging     = 7
    production  = 7
  }
}

variable "business_kpi_thresholds" {
  description = "Map of business KPIs and their thresholds"
  type        = map(number)
  default     = {}
}

variable "monthly_budget_amount" {
  description = "Monthly budget amount in USD"
  type        = number
}

# Outputs
output "alert_topic_arn" {
  description = "ARN of the SNS topic for alerts"
  value       = aws_sns_topic.alerts.arn
}

output "log_group_names" {
  description = "Names of the CloudWatch log groups"
  value = {
    application = aws_cloudwatch_log_group.application.name
    nginx       = aws_cloudwatch_log_group.nginx.name
  }
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "canary_name" {
  description = "Name of the Synthetics canary"
  value       = aws_synthetics_canary.healthcheck.name
}
