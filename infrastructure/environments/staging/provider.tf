provider "aws" {
  region = "eu-west-2"

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.app_name
      ManagedBy   = "Terraform"
    }
  }
}

provider "aws" {
  alias  = "eu-west-2"
  region = "eu-west-2"
}

terraform {
  required_providers {
    aws = {
      source  = "opentofu/aws"
      version = "~> 4.0"
    }
  }
}