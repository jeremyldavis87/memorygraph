#!/bin/bash

# Setup ECR repositories for MemoryGraph
# AWS Account: 969325212479

set -e

echo "🐳 Setting up ECR repositories..."

# Set AWS profile
export AWS_PROFILE=jeremy_personal_local
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=969325212479

# Login to ECR
echo "🔐 Logging in to ECR..."
aws ecr get-login-password --region us-east-1 | podman login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Create ECR repositories
echo "📦 Creating ECR repositories..."

# Backend repository
aws ecr create-repository \
    --repository-name memorygraph-backend \
    --region us-east-1 \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    || echo "Repository already exists"

# Frontend repository
aws ecr create-repository \
    --repository-name memorygraph-frontend \
    --region us-east-1 \
    --image-scanning-configuration scanOnPush=true \
    --encryption-configuration encryptionType=AES256 \
    || echo "Repository already exists"

echo "✅ ECR repositories created"

# Build and push images
echo "🔨 Building and pushing Podman images..."

# Backend
cd backend
podman build -t memorygraph-backend:latest .
podman tag memorygraph-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-backend:latest
podman push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-backend:latest

# Frontend
cd ../frontend
podman build -t memorygraph-frontend:latest .
podman tag memorygraph-frontend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-frontend:latest
podman push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-frontend:latest

echo "✅ Podman images pushed to ECR"

echo "🎉 ECR setup complete!"
echo "Backend image: $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-backend:latest"
echo "Frontend image: $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/memorygraph-frontend:latest"

cd ..
