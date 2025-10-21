# MemoryGraph AWS Deployment Guide

## Overview
This guide will help you deploy the MemoryGraph application to AWS account `969325212479` using Terraform and ECS Fargate.

## Prerequisites
- ✅ AWS CLI configured with profile `jeremy_personal_local`
- ✅ Docker installed and running
- ✅ Terraform installed (>= 1.0)
- ✅ Access to AWS account 969325212479

## Architecture
The deployment creates the following AWS resources:
- **VPC** with public/private subnets across 2 AZs
- **RDS PostgreSQL** database in private subnets
- **ElastiCache Redis** cluster for caching
- **ECS Fargate** cluster for containerized applications
- **Application Load Balancer** for traffic distribution
- **ECR repositories** for Docker images
- **CloudWatch** for logging and monitoring

## Deployment Steps

### 1. Verify AWS Configuration
```bash
# Check AWS profile
aws sts get-caller-identity --profile jeremy_personal_local

# Should return account: 969325212479
```

### 2. Deploy Infrastructure
```bash
# Run the deployment script
./deploy.sh
```

This will:
- Initialize Terraform
- Plan the infrastructure deployment
- Deploy all AWS resources
- Update environment files with actual endpoints

### 3. Build and Push Docker Images
```bash
# Setup ECR repositories and push images
./setup-ecr.sh
```

This will:
- Create ECR repositories
- Build Docker images for backend and frontend
- Push images to ECR

### 4. Update ECS Task Definition
After the infrastructure is deployed, you'll need to update the ECS task definition with the actual ECR image URIs:

```bash
# Get the ECR repository URLs
cd infrastructure
terraform output backend_ecr_repository
terraform output frontend_ecr_repository
```

### 5. Deploy Application Updates
```bash
# Update ECS service with new task definition
aws ecs update-service \
  --cluster memorygraph-cluster \
  --service memorygraph-service \
  --force-new-deployment \
  --profile jeremy_personal_local
```

## Configuration Files

### Environment Variables
- `.env.production` - Production environment configuration
- `infrastructure/terraform.tfvars` - Terraform variables

### Key Configuration Values
- **AWS Account**: 969325212479
- **Region**: us-west-2
- **Database**: PostgreSQL 15.4 on RDS
- **Cache**: Redis on ElastiCache
- **Compute**: ECS Fargate
- **Load Balancer**: Application Load Balancer

## Security Considerations

### Database Security
- RDS instance in private subnets
- Security groups restrict access to ECS tasks only
- Encryption at rest enabled

### Network Security
- Public subnets for load balancer
- Private subnets for application and database
- Security groups with minimal required access

### Secrets Management
- Database password in Terraform variables
- API keys in environment variables
- Consider using AWS Secrets Manager for production

## Monitoring and Logging

### CloudWatch Logs
- ECS task logs: `/ecs/memorygraph`
- Retention: 7 days

### Health Checks
- Application Load Balancer health checks on `/health` endpoint
- RDS automated backups enabled

## Cost Optimization

### Resource Sizing
- RDS: db.t3.micro (free tier eligible)
- ElastiCache: cache.t3.micro (free tier eligible)
- ECS: 512 CPU, 1024 MB memory

### Lifecycle Policies
- ECR lifecycle policies to keep only 10 latest images
- CloudWatch log retention: 7 days

## Troubleshooting

### Common Issues
1. **ECS tasks not starting**: Check CloudWatch logs
2. **Database connection issues**: Verify security groups
3. **Load balancer health checks failing**: Check application health endpoint

### Useful Commands
```bash
# Check ECS service status
aws ecs describe-services --cluster memorygraph-cluster --services memorygraph-service

# View CloudWatch logs
aws logs describe-log-streams --log-group-name /ecs/memorygraph

# Check RDS status
aws rds describe-db-instances --db-instance-identifier memorygraph-db
```

## Post-Deployment

### Domain Configuration
1. Update DNS records to point to the ALB DNS name
2. Update CORS origins in Terraform variables
3. Consider SSL certificate for HTTPS

### Application Updates
1. Build new Docker images
2. Push to ECR
3. Update ECS service

## Cleanup
To remove all resources:
```bash
cd infrastructure
terraform destroy -var-file="terraform.tfvars"
```

## Support
For issues or questions, check:
- CloudWatch logs for application errors
- ECS service events for deployment issues
- RDS logs for database connectivity problems
