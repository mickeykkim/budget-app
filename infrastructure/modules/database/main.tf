# modules/database/main.tf

# KMS key for RDS encryption
resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Name        = "${var.app_name}-${var.environment}-rds"
    Environment = var.environment
  }
}

# Random password for RDS
resource "random_password" "rds" {
  length  = 32
  special = true
}

# Store password in Secrets Manager
resource "aws_secretsmanager_secret" "rds" {
  name        = "${var.app_name}-${var.environment}-rds"
  description = "RDS master password"
  kms_key_id  = aws_kms_key.rds.id
}

resource "aws_secretsmanager_secret_version" "rds" {
  secret_id = aws_secretsmanager_secret.rds.id
  secret_string = jsonencode({
    username = "postgres"
    password = random_password.rds.result
    host     = aws_db_instance.main.address
    port     = 5432
    dbname   = "budget_app"
  })
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name        = "${var.app_name}-${var.environment}"
  description = "Subnet group for RDS instance"
  subnet_ids  = var.subnet_ids

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
  }
}

# Parameter Group
resource "aws_db_parameter_group" "main" {
  family = "postgres14"
  name   = "${var.app_name}-${var.environment}"

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_duration"
    value = "1"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000" # Log queries taking more than 1 second
  }

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
  }
}

# Option Group
resource "aws_db_option_group" "main" {
  name                 = "${var.app_name}-${var.environment}"
  engine_name          = "postgres"
  major_engine_version = "14"

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
  }
}

# Security Group
resource "aws_security_group" "database" {
  name        = "${var.app_name}-${var.environment}-database"
  description = "Security group for RDS database"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
    description     = "Allow PostgreSQL access from ECS tasks"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.app_name}-${var.environment}-database"
    Environment = var.environment
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${var.app_name}-${var.environment}"

  # Engine configuration
  engine                = "postgres"
  engine_version        = var.engine_version
  instance_class        = "db.t3.micro"
  allocated_storage     = 20
  max_allocated_storage = 20 # Limit auto-scaling

  # Database configuration
  db_name  = "budget_app"
  username = "postgres"
  password = random_password.rds.result
  port     = 5432

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.database.id]
  multi_az               = false # No high availability needed

  # Backup configuration
  backup_retention_period = lookup(var.backup_retention_days, var.environment, 7)
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  # Enhanced monitoring
  monitoring_interval                   = 0 # Disable enhanced monitoring
  performance_insights_enabled          = false
  monitoring_role_arn                   = aws_iam_role.rds_monitoring.arn
  performance_insights_retention_period = 7
  performance_insights_kms_key_id       = aws_kms_key.rds.id

  # Storage configuration
  storage_type      = "gp3"
  storage_encrypted = true
  kms_key_id        = aws_kms_key.rds.arn
  iops              = var.environment == "production" ? 3000 : 0

  # Parameter and option groups
  parameter_group_name = aws_db_parameter_group.main.name
  option_group_name    = aws_db_option_group.main.name

  # Deletion protection
  deletion_protection       = var.environment == "production"
  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = var.environment != "production" ? null : "${var.app_name}-${var.environment}-final-${formatdate("YYYY-MM-DD-hh-mm", timestamp())}"

  # Auto minor version upgrades
  auto_minor_version_upgrade  = var.environment != "production"
  allow_major_version_upgrade = false

  # Enhanced Monitoring Role
  depends_on = [aws_iam_role_policy_attachment.rds_monitoring]

  tags = {
    Name        = "${var.app_name}-${var.environment}"
    Environment = var.environment
  }
}

# Read Replica (for production)
resource "aws_db_instance" "replica" {
  count = var.environment == "production" ? 1 : 0

  identifier = "${var.app_name}-${var.environment}-replica"

  instance_class      = var.replica_instance_class
  replicate_source_db = aws_db_instance.main.id

  vpc_security_group_ids = [aws_security_group.database.id]

  auto_minor_version_upgrade = false
  maintenance_window         = "Tue:04:00-Tue:05:00"

  backup_retention_period = 0
  skip_final_snapshot     = true

  monitoring_interval                   = 30
  monitoring_role_arn                   = aws_iam_role.rds_monitoring.arn
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  performance_insights_kms_key_id       = aws_kms_key.rds.id

  tags = {
    Name        = "${var.app_name}-${var.environment}-replica"
    Environment = var.environment
  }
}

# Enhanced Monitoring IAM Role
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.app_name}-${var.environment}-rds-monitoring"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.app_name}-${var.environment}-database-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "80"
  alarm_description   = "Database CPU utilization is too high"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}

resource "aws_cloudwatch_metric_alarm" "database_memory" {
  alarm_name          = "${var.app_name}-${var.environment}-database-memory"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "100000000" # 100MB in bytes
  alarm_description   = "Database freeable memory is too low"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}

resource "aws_cloudwatch_metric_alarm" "database_disk" {
  alarm_name          = "${var.app_name}-${var.environment}-database-disk"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = "300"
  statistic           = "Average"
  threshold           = "5000000000" # 5GB in bytes
  alarm_description   = "Database free storage space is too low"
  alarm_actions       = [var.sns_topic_arn]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
}
