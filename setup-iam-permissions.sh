#!/bin/bash

# Setup IAM permissions for MemoryGraph deployment
# This script creates and attaches the necessary IAM policy to the MemoryGraph-Deployer group

set -e

echo "🔐 Setting up IAM permissions for MemoryGraph deployment..."

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

# Policy name and group name
POLICY_NAME="MemoryGraph-Deployer-Policy"
GROUP_NAME="MemoryGraph-Deployer"

echo "📋 Creating IAM policy: $POLICY_NAME"

# Create the IAM policy
aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document file://iam-policy-memorygraph-deployer.json \
    --description "Comprehensive permissions for MemoryGraph infrastructure deployment" \
    || echo "Policy may already exist, continuing..."

# Get the policy ARN
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${POLICY_NAME}"

echo "📋 Policy ARN: $POLICY_ARN"

# Attach the policy to the MemoryGraph-Deployer group
echo "🔗 Attaching policy to group: $GROUP_NAME"
aws iam attach-group-policy \
    --group-name "$GROUP_NAME" \
    --policy-arn "$POLICY_ARN" \
    || echo "Policy may already be attached, continuing..."

echo "✅ IAM permissions setup complete!"
echo ""
echo "📋 Summary:"
echo "   - Policy: $POLICY_NAME"
echo "   - Group: $GROUP_NAME"
echo "   - Policy ARN: $POLICY_ARN"
echo ""
echo "🔧 The MemoryGraph-Deployer group now has permissions for:"
echo "   - EC2 (VPC, subnets, security groups, tags)"
echo "   - RDS (database instances)"
echo "   - ElastiCache (Redis clusters)"
echo "   - ECS (clusters, services, task definitions)"
echo "   - ELB (application load balancers)"
echo "   - ECR (container repositories)"
echo "   - IAM (roles and policies)"
echo "   - CloudWatch (logs and monitoring)"
echo "   - Secrets Manager (secret access)"
echo "   - S3 (Terraform state buckets)"
echo ""
echo "🚀 You can now run the GitHub Actions workflow again!"
