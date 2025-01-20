# environments/production/terraform.tfvars
environment = "production"
app_name    = "budget-app"
vpc_cidr    = "10.0.0.0/16"
alert_email_addresses = ["ops@example.com", "oncall@example.com"]  # TODO: Add actual alert email address
domain_name = "budget-app.example.com"  # TODO: Add domain url address
container_image = "your-repository/budget-app:latest"  # TODO: Add actual image location
route53_zone_id = "ZONE_ID" # TODO: Replace with actual zone ID
certificate_arn = "CERT_ARN" # TODO: Replace with actual certificate ARN