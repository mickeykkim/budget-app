#!/bin/bash
set -e

# Get AWS credentials
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=eu-west-2

# ECR login
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and push backend
cd backend || exit 1
docker build -t budget-app-backend -f Dockerfile.prod .
cd ..

# Build and push frontend
cd frontend || exit 1
docker build -t budget-app-frontend -f Dockerfile.prod .
cd ..

# Tag and push images
docker tag budget-app-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/budget-app-frontend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/budget-app-frontend:latest

docker tag budget-app-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/budget-app-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/budget-app-backend:latest

# Update ECS service
aws ecs update-service --cluster budget-app --service budget-app-service --force-new-deployment
