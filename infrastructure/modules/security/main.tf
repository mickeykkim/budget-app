# modules/security/main.tf

# KMS Master Keys
resource "aws_kms_key" "main" {
  description             = "${var.app_name}-${var.environment}-master-key"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  multi_region           = var.environment == "production"

  # Key policy allows both root and specific roles
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow ECS to use the key"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_role.ecs_task_role.arn
        }
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.app_name}-${var.environment}-master-key"
    Environment = var.environment
  }
}

# SSM Parameters
resource "aws_ssm_parameter" "database_url" {
  name        = "/${var.environment}/${var.app_name}/database_url"
  description = "Database connection URL"
  type        = "SecureString"
  value       = var.database_url
  key_id      = aws_kms_key.main.id

  tags = {
    Environment = var.environment
  }
}

resource "aws_ssm_parameter" "jwt_secret" {
  name        = "/${var.environment}/${var.app_name}/jwt_secret"
  description = "JWT signing secret"
  type        = "SecureString"
  value       = random_password.jwt_secret.result
  key_id      = aws_kms_key.main.id

  tags = {
    Environment = var.environment
  }
}

# Random password for JWT
resource "random_password" "jwt_secret" {
  length  = 32
  special = true
}

# IAM Roles and Policies

# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.app_name}-${var.environment}-ecs-task-role"

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
    Name        = "${var.app_name}-${var.environment}-ecs-task-role"
    Environment = var.environment
  }
}

# Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.app_name}-${var.environment}-task-execution-role"

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
    Name        = "${var.app_name}-${var.environment}-task-execution-role"
    Environment = var.environment
  }
}

# Task Role Policies
resource "aws_iam_role_policy" "ecs_task_ssm" {
  name = "${var.app_name}-${var.environment}-task-ssm-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.environment}/${var.app_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_kms" {
  name = "${var.app_name}-${var.environment}-task-kms-policy"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*"
        ]
        Resource = [aws_kms_key.main.arn]
      }
    ]
  })
}

# Task Execution Role Policies
resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_task_execution_ssm" {
  name = "${var.app_name}-${var.environment}-task-execution-ssm-policy"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:parameter/${var.environment}/${var.app_name}/*"
        ]
      }
    ]
  })
}

# Security Hub
resource "aws_securityhub_account" "main" {
  count = var.environment == "production" ? 1 : 0
}

resource "aws_securityhub_standards_subscription" "cis" {
  count         = var.environment == "production" ? 1 : 0
  standards_arn = "arn:aws:securityhub:${data.aws_region.current.name}::standards/cis-aws-foundations-benchmark/v1.2.0"
  depends_on    = [aws_securityhub_account.main]
}

# Password Policy
resource "aws_iam_account_password_policy" "strict" {
  count                          = var.environment == "production" ? 1 : 0
  minimum_password_length        = 14
  require_lowercase_characters   = true
  require_numbers               = true
  require_uppercase_characters   = true
  require_symbols               = true
  allow_users_to_change_password = true
  max_password_age              = 90
  password_reuse_prevention     = 24
}

# CloudWatch Logs Encryption
resource "aws_kms_key" "cloudwatch" {
  description             = "${var.app_name}-${var.environment}-cloudwatch"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${data.aws_region.current.name}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt*",
          "kms:Decrypt*",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:Describe*"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.app_name}-${var.environment}-cloudwatch"
    Environment = var.environment
  }
}

# AWS Config
resource "aws_config_configuration_recorder" "main" {
  count = var.environment == "production" ? 1 : 0
  name  = "${var.app_name}-${var.environment}-config"

  recording_group {
    all_supported = true
    include_global_resources = true
  }

  role_arn = aws_iam_role.config_role[0].arn
}

resource "aws_iam_role" "config_role" {
  count = var.environment == "production" ? 1 : 0
  name  = "${var.app_name}-${var.environment}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      }
    ]
  })
}

# GuardDuty
resource "aws_guardduty_detector" "main" {
  count  = var.environment == "production" ? 1 : 0
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = true
      }
    }
  }
}

# Service Control Policies (if using AWS Organizations)
resource "aws_organizations_policy" "require_mfa" {
  count = var.environment == "production" ? 1 : 0
  name  = "${var.app_name}-require-mfa"
  content = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "RequireMFA"
        Effect = "Deny"
        NotAction = [
          "iam:CreateVirtualMFADevice",
          "iam:EnableMFADevice",
          "iam:GetUser",
          "iam:ListMFADevices",
          "iam:ListVirtualMFADevices",
          "iam:ResyncMFADevice",
          "sts:GetSessionToken"
        ]
        Resource = "*"
        Condition = {
          BoolIfExists = {
            "aws:MultiFactorAuthPresent" = "false"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "config" {
  count      = var.environment == "production" ? 1 : 0
  role       = aws_iam_role.config_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
}
