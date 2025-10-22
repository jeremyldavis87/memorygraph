#!/bin/bash

# MemoryGraph AWS Deployment Script
# AWS Account: 969325212479

set -e

echo "🚀 Starting MemoryGraph AWS Deployment..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity --profile jeremy_personal_local > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured or invalid credentials"
    echo "Please run: aws configure --profile jeremy_personal_local"
    exit 1
fi

# Set AWS profile
export AWS_PROFILE=jeremy_personal_local
export AWS_REGION=us-west-2

echo "✅ AWS Profile: jeremy_personal_local"
echo "✅ AWS Region: us-west-2"

# Navigate to infrastructure directory
cd infrastructure

# Initialize Terraform
echo "🔧 Initializing Terraform..."
terraform init

# Plan the deployment
echo "📋 Planning Terraform deployment..."
terraform plan -var-file="terraform.tfvars"

# Ask for confirmation
read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

# Apply the infrastructure
echo "🏗️  Deploying infrastructure..."
terraform apply -var-file="terraform.tfvars" -auto-approve

# Get outputs
echo "📊 Getting deployment outputs..."
ALB_DNS=$(terraform output -raw alb_dns_name)
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)
REDIS_ENDPOINT=$(terraform output -raw redis_endpoint)

echo "✅ Deployment completed!"
echo "🌐 Application Load Balancer: $ALB_DNS"
echo "🗄️  RDS Endpoint: $RDS_ENDPOINT"
echo "🔴 Redis Endpoint: $REDIS_ENDPOINT"

# Update environment files with actual endpoints
echo "📝 Updating environment files..."
cd ..

# Update production environment file
sed -i "s/memorygraph-db.xxxxx.us-west-2.rds.amazonaws.com/$RDS_ENDPOINT/g" .env.production
sed -i "s/memorygraph-redis.xxxxx.cache.amazonaws.com/$REDIS_ENDPOINT/g" .env.production

echo "✅ Environment files updated with actual endpoints"

# Build and push Docker images
echo "🐳 Building and pushing Docker images..."

# Build backend image
cd backend
docker build -t memorygraph-backend:latest .
docker tag memorygraph-backend:latest 969325212479.dkr.ecr.us-west-2.amazonaws.com/memorygraph-backend:latest

# Build frontend image
cd ../frontend
docker build -t memorygraph-frontend:latest .
docker tag memorygraph-frontend:latest 969325212479.dkr.ecr.us-west-2.amazonaws.com/memorygraph-frontend:latest

echo "✅ Docker images built and tagged"

echo "🎉 Deployment preparation complete!"
echo "Next steps:"
echo "1. Create ECR repositories in AWS Console"
echo "2. Push Docker images to ECR"
echo "3. Update ECS task definitions with ECR image URIs"
echo "4. Deploy the application"

cd ..
