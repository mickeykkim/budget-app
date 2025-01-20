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
  region = "eu-west-2"  # Required for ACM certificates with CloudFront
}
