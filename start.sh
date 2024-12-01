#!/bin/bash
set -e

echo "Starting containers..."
docker-compose up --build -d

echo "Waiting for PostgreSQL to be ready..."
until docker-compose exec postgres pg_isready -U budget_app_user -d budget_app_local; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "Waiting for LocalStack to be ready..."
until nc -z localhost 4566; do
    sleep 1
done

echo "Initializing LocalStack resources..."
docker-compose exec localstack bash /localstack/init-aws.sh
docker-compose exec backend bash init-db.sh

echo "Setup complete! Your development environment is ready."
