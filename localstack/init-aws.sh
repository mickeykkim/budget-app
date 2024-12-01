#!/bin/bash
# localstack/init-aws.sh

# Configure AWS CLI for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=eu-west-1

# Function to check if LocalStack is ready
check_localstack() {
    # Try a simple AWS command
    if awslocal sts get-caller-identity >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
COUNTER=0
RETRY_LIMIT=45

until check_localstack || [ $COUNTER -eq $RETRY_LIMIT ]; do
    echo "Attempt $COUNTER of $RETRY_LIMIT..."
    ((COUNTER++))
    sleep 2
done

if [ $COUNTER -eq $RETRY_LIMIT ]; then
    echo "LocalStack failed to become ready in time"
    exit 1
fi

echo "LocalStack is ready! Setting up resources..."

# Create S3 bucket
echo "Creating S3 bucket..."
if awslocal s3 mb s3://budget-app-frontend 2>/dev/null; then
    echo "S3 bucket created successfully"
else
    echo "S3 bucket creation failed or bucket already exists"
fi

# Create SQS queue
echo "Creating SQS queue..."
if awslocal sqs create-queue --queue-name budget-app-queue 2>/dev/null; then
    echo "SQS queue created successfully"
else
    echo "SQS queue creation failed or queue already exists"
fi

# Create EventBridge rule
echo "Creating EventBridge rule..."
if awslocal events put-rule \
    --name budget-app-daily \
    --schedule-expression "rate(1 day)" 2>/dev/null; then
    echo "EventBridge rule created successfully"
else
    echo "EventBridge rule creation failed or rule already exists"
fi

# Create IAM role for Lambda
echo "Creating IAM role..."
if awslocal iam create-role \
    --role-name lambda-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }' 2>/dev/null; then
    echo "IAM role created successfully"
else
    echo "IAM role creation failed or role already exists"
fi

# Attach basic execution policy to the role
echo "Attaching IAM policy..."
if awslocal iam put-role-policy \
    --role-name lambda-role \
    --policy-name lambda-execution \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }' 2>/dev/null; then
    echo "IAM policy attached successfully"
else
    echo "IAM policy attachment failed or policy already exists"
fi

echo "LocalStack initialization complete!"
