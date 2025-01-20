# modules/security/variables.tf

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "database_url" {
  description = "Database connection URL"
  type        = string
  sensitive   = true
}

variable "enable_security_hub" {
  description = "Enable Security Hub and its standards"
  type        = bool
  default     = true
}

variable "enable_guardduty" {
  description = "Enable GuardDuty"
  type        = bool
  default     = true
}

variable "enable_config" {
  description = "Enable AWS Config"
  type        = bool
  default     = true
}

variable "kms_key_deletion_window" {
  description = "Deletion window for KMS keys in days"
  type        = number
  default     = 7
}

variable "password_policy_max_age" {
  description = "Maximum age of passwords in days"
  type        = number
  default     = 90
}

variable "password_policy_reuse_prevention" {
  description = "Number of previous passwords that users are prevented from reusing"
  type        = number
  default     = 24
}
