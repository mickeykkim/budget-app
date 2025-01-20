# environments/staging/terraform.tfvars
environment = "staging"
app_name    = "budget-app"
vpc_cidr    = "10.1.0.0/16"  # Different CIDR from production
alert_email_addresses = ["devops@example.com", "dev-team@example.com"]  # TODO: Add actual alert email addresses
container_image = "your-repository/budget-app:latest"  # TODO: Add actual image location