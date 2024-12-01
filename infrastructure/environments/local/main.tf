module "budget_app" {
  source = "../../modules/budget_app"

  environment = "local"
  app_name    = "budget-app"
}

# Store state locally for development
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
