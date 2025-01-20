# environments/development/terraform.tfvars
environment = "development"
app_name    = "budget-app"
vpc_cidr    = "10.2.0.0/16"  # Different CIDR from staging and production
alert_email_addresses = ["dev-team@example.com"]  # TODO: Add actual alert email address
container_image = "your-repository/budget-app:latest"  # TODO: Add actual image location
