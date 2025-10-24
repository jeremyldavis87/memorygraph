#!/bin/bash

# Setup ECR repositories for MemoryGraph Graph Services
# AWS Account: 969325212479

set -e

echo "🐳 Setting up ECR repositories for graph services..."

# Set AWS profile and region
export AWS_PROFILE=jeremy_personal_local
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=969325212479

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repositories for graph services
echo "📦 Creating ECR repositories for graph services..."

# Extractor service repository
aws ecr create-repository \
    --repository-name memorygraph-dev-extractor-service \
    --region us-east-1 \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    || echo "Repository already exists"

# Inserter service repository
aws ecr create-repository \
    --repository-name memorygraph-dev-inserter-service \
    --region us-east-1 \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    || echo "Repository already exists"

# Retriever service repository
aws ecr create-repository \
    --repository-name memorygraph-dev-retriever-service \
    --region us-east-1 \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    || echo "Repository already exists"

echo "✅ ECR repositories for graph services created"

echo "🎉 Graph services ECR setup complete!"
echo "Extractor service: $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-dev-extractor-service"
echo "Inserter service: $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-dev-inserter-service"
echo "Retriever service: $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-dev-retriever-service"
