# Secure Configuration Guide

## Important Security Notes

The configuration files in this repository contain placeholder values for sensitive information. Before deploying to AWS, you must update the following files with your actual credentials:

### Files to Update Before Deployment

1. **`.env`** - Development environment
2. **`.env.production`** - Production environment  
3. **`infrastructure/terraform.tfvars`** - Terraform variables

### Required Values to Replace

#### API Keys
- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key

#### Database Credentials
- `db_password` - Strong database password for RDS
- `DATABASE_URL` - Will be auto-generated after RDS deployment

#### Security Keys
- `SECRET_KEY` - JWT secret key for authentication
- `secret_key` - Same value for Terraform

### Example Secure Configuration

```bash
# .env.production
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here
SECRET_KEY=YourSecureJWTSecretKey2024!Production
```

```hcl
# infrastructure/terraform.tfvars
openai_api_key = "sk-proj-your-actual-openai-key-here"
secret_key = "YourSecureJWTSecretKey2024!Production"
db_password = "YourSecureDatabasePassword2024!"
```

### Security Best Practices

1. **Never commit real API keys to version control**
2. **Use strong, unique passwords for production**
3. **Rotate secrets regularly**
4. **Consider using AWS Secrets Manager for production**
5. **Use environment-specific configuration files**

### AWS Secrets Manager (Recommended for Production)

For production deployments, consider using AWS Secrets Manager:

```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "memorygraph/openai-api-key" \
  --secret-string "your-openai-key" \
  --profile jeremy_personal_local

aws secretsmanager create-secret \
  --name "memorygraph/jwt-secret" \
  --secret-string "your-jwt-secret" \
  --profile jeremy_personal_local
```

Then update your ECS task definition to retrieve secrets from AWS Secrets Manager instead of environment variables.
