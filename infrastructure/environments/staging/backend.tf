# environments/staging/backend.tf
terraform {
  backend "s3" {
    bucket         = "budget-app-terraform-state"
    key            = "staging/terraform.tfstate"
    region         = "eu-west-2"
    dynamodb_table = "budget-app-terraform-locks"
    encrypt        = true
  }
}
