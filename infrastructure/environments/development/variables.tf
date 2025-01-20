# environments/development/variables.tf
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
}

variable "route53_zone_id" {
  description = "Route 53 hosted zone ID"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate"
  type        = string
}

variable "alert_email_addresses" {
  description = "List of email addresses for alerts"
  type        = list(string)
}

variable "container_image" {
  description = "Container image to deploy"
  type        = string
}
