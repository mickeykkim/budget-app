locals {
  environment_config = {
    instance_type = "t3.micro"
    min_capacity  = 1
    max_capacity  = 2
    desired_count = 1
    storage_size  = 20
  }
}
