#!/bin/bash
set -e

echo "Starting containers..."
docker-compose up --build -d

echo "Waiting for PostgreSQL to be ready..."
until docker-compose exec -T postgres pg_isready -U budget_app_user -d budget_app_local; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "Waiting for LocalStack to be ready..."
until nc -z localhost 4566; do
    echo "Waiting for LocalStack..."
    sleep 1
done

echo "Running database migrations..."
docker-compose exec -T backend alembic upgrade head

echo "Initializing LocalStack resources..."
docker-compose exec -T localstack bash /localstack/init-aws.sh

echo "Initializing database..."
docker-compose exec -T backend python init-db.py

echo "Setup complete! Your development environment is ready."
