#!/bin/bash

# Function to run alembic migrations
run_migrations() {
    echo "Running database migrations..."
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo "Migrations completed successfully"
    else
        echo "Migration failed"
        return 1
    fi
}

# Function to create test data
create_test_data() {
    echo "Creating test data..."
    python -c "
from app.schemas.user import UserCreate
from app.services.user_service import UserService
from app.core.database import SessionLocal

db = SessionLocal()
try:
    user_service = UserService(db)
    user_data = UserCreate(email='test@example.com', password='testpassword123')
    if not user_service.get_by_email(user_data.email):
        user = user_service.create(user_data)
        print(f'Created user: {user.email}')
    else:
        print('User already exists')
finally:
    db.close()
    "
}

# Main initialization sequence
echo "Starting database initialization..."

# Run migrations
run_migrations
if [ $? -ne 0 ]; then
    echo "Database initialization failed at migrations step"
    exit 1
fi

# Create test data
create_test_data
if [ $? -ne 0 ]; then
    echo "Database initialization failed at test data creation step"
    exit 1
fi

echo "Database initialization completed successfully!"
