# environments/production/main.tf
module "security" {
  source = "../../modules/security"

  environment   = var.environment
  app_name      = var.app_name
  database_url  = module.database.endpoint

  enable_security_hub = true
  enable_guardduty   = true
  enable_config      = true
}

module "networking" {
  source = "../../modules/networking"

  environment            = var.environment
  app_name              = var.app_name
  vpc_cidr              = var.vpc_cidr
  cloudwatch_kms_key_arn = module.security.cloudwatch_kms_key_arn
}

module "container" {
  source = "../../modules/container"

  environment         = var.environment
  app_name           = var.app_name
  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
  public_subnet_ids  = module.networking.public_subnet_ids
  certificate_arn    = var.certificate_arn
  container_image    = var.container_image

  task_role_arn          = module.security.ecs_task_role_arn
  task_execution_role_arn = module.security.ecs_task_execution_role_arn
  cloudwatch_kms_key_arn  = module.security.cloudwatch_kms_key_arn

  # Production-specific settings
  task_cpu       = 1024
  task_memory    = 2048
  desired_count  = 2
  min_capacity   = 2
  max_capacity   = 8
  container_port = 8000

  depends_on = [module.security, module.networking]
}

module "database" {
  source = "../../modules/database"

  environment            = var.environment
  app_name              = var.app_name
  vpc_id                = module.networking.vpc_id
  subnet_ids            = module.networking.private_subnet_ids
  ecs_security_group_id = module.container.ecs_security_group_id
  sns_topic_arn         = module.monitoring.alert_topic_arn

  # Production-specific settings
  instance_class        = "db.r6g.large"
  allocated_storage     = 100
  max_allocated_storage = 1000
  deletion_protection   = true

  depends_on = [module.networking]
}

module "frontend" {
  source = "../../modules/frontend"

  environment      = var.environment
  app_name        = var.app_name
  domain_name     = var.domain_name
  route53_zone_id = var.route53_zone_id
  enable_shield   = true # Enable Shield for production
}

module "monitoring" {
  source = "../../modules/monitoring"

  environment              = var.environment
  app_name                = var.app_name
  vpc_id                  = module.networking.vpc_id
  private_subnet_ids      = module.networking.private_subnet_ids
  ecs_cluster_name        = "${var.app_name}-${var.environment}"
  ecs_service_name        = "${var.app_name}-${var.environment}"
  alb_arn_suffix          = module.container.alb_dns_name
  db_instance_identifier  = "${var.app_name}-${var.environment}"
  cloudwatch_kms_key_arn  = module.security.cloudwatch_kms_key_arn
  sns_kms_key_arn        = module.security.kms_key_arn
  alert_email_addresses   = var.alert_email_addresses
  app_url                = "https://${var.domain_name}"
  monitoring_bucket      = "${var.app_name}-${var.environment}-monitoring"
  monthly_budget_amount  = 50 # $50 monthly budget for production

  depends_on = [
    module.database,
    module.container,
    module.security
  ]
}