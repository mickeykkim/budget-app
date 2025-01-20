# modules/networking/variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "cloudwatch_kms_key_arn" {
  description = "KMS key ARN for CloudWatch encryption"
  type        = string
}
