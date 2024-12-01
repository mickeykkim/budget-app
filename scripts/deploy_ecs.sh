#!/bin/bash
set -e

# Build and push Docker image
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com
docker build -t budget-app .
docker tag budget-app:latest ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com/budget-app:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com/budget-app:latest

# Update ECS service
aws ecs update-service --cluster budget-app --service budget-app-service --force-new-deployment
