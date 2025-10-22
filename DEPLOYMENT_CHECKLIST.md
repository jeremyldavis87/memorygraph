# MemoryGraph AWS Deployment Checklist

## Pre-Deployment ✅
- [x] AWS CLI configured with profile `jeremy_personal_local`
- [x] AWS account access verified (969325212479)
- [x] Terraform configuration updated for target account
- [x] Environment variables configured
- [x] Docker images ready for ECR
- [x] Health check endpoint implemented (`/health`)

## Infrastructure Deployment
- [ ] Run `./deploy.sh` to deploy infrastructure
- [ ] Verify all AWS resources created successfully
- [ ] Check RDS endpoint and connectivity
- [ ] Verify Redis cluster is running
- [ ] Confirm ALB is healthy

## Application Deployment
- [ ] Run `./setup-ecr.sh` to build and push Docker images
- [ ] Update ECS task definition with ECR image URIs
- [ ] Deploy ECS service
- [ ] Verify application is accessible via ALB

## Post-Deployment Verification
- [ ] Test health check endpoint: `http://<ALB_DNS>/health`
- [ ] Test API endpoints: `http://<ALB_DNS>/api/v1/`
- [ ] Verify database connectivity
- [ ] Check CloudWatch logs for any errors
- [ ] Test CORS configuration

## Security Verification
- [ ] RDS instance in private subnets
- [ ] Security groups properly configured
- [ ] No direct internet access to database
- [ ] SSL/TLS configuration (if using custom domain)

## Monitoring Setup
- [ ] CloudWatch logs configured
- [ ] Health check monitoring
- [ ] Database backup verification
- [ ] Cost monitoring alerts

## Domain Configuration (Optional)
- [ ] Purchase/configure domain name
- [ ] Set up Route 53 hosted zone
- [ ] Configure SSL certificate
- [ ] Update CORS origins in Terraform
- [ ] Point domain to ALB

## Final Steps
- [ ] Update documentation with actual endpoints
- [ ] Test full application functionality
- [ ] Set up monitoring and alerting
- [ ] Create backup and disaster recovery plan
