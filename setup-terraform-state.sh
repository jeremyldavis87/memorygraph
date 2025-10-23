#!/bin/bash

# Setup S3 buckets for Terraform state storage
# AWS Account: 969325212479

set -e

echo "🗄️ Setting up Terraform state S3 buckets..."

# Set AWS profile and region
export AWS_PROFILE=jeremy_personal_local
export AWS_REGION=us-east-1
export AWS_ACCOUNT_ID=969325212479

# Check if AWS CLI is configured
if ! aws sts get-caller-identity --profile jeremy_personal_local > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured or invalid credentials"
    echo "Please run: aws configure --profile jeremy_personal_local"
    exit 1
fi

echo "✅ AWS Profile: jeremy_personal_local"
echo "✅ AWS Region: us-east-1"
echo "✅ AWS Account: $AWS_ACCOUNT_ID"

# Create S3 buckets for Terraform state
echo "📦 Creating S3 buckets for Terraform state..."

# Dev environment bucket
echo "Creating dev state bucket..."
aws s3 mb s3://memorygraph-terraform-state-dev --region us-east-1 || echo "Bucket already exists"

# Prod environment bucket  
echo "Creating prod state bucket..."
aws s3 mb s3://memorygraph-terraform-state-prod --region us-east-1 || echo "Bucket already exists"

# Enable versioning on both buckets
echo "🔒 Enabling versioning on state buckets..."
aws s3api put-bucket-versioning --bucket memorygraph-terraform-state-dev --versioning-configuration Status=Enabled
aws s3api put-bucket-versioning --bucket memorygraph-terraform-state-prod --versioning-configuration Status=Enabled

# Enable server-side encryption
echo "🔐 Enabling server-side encryption..."
aws s3api put-bucket-encryption --bucket memorygraph-terraform-state-dev --server-side-encryption-configuration '{
    "Rules": [
        {
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }
    ]
}'

aws s3api put-bucket-encryption --bucket memorygraph-terraform-state-prod --server-side-encryption-configuration '{
    "Rules": [
        {
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }
    ]
}'

# Block public access
echo "🛡️ Blocking public access..."
aws s3api put-public-access-block --bucket memorygraph-terraform-state-dev --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
aws s3api put-public-access-block --bucket memorygraph-terraform-state-prod --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "✅ Terraform state buckets created and configured!"
echo "📋 Buckets created:"
echo "   - memorygraph-terraform-state-dev"
echo "   - memorygraph-terraform-state-prod"
echo ""
echo "🔧 Next steps:"
echo "   1. Run the GitHub Actions workflow again"
echo "   2. The Terraform infrastructure deployment should now work"
