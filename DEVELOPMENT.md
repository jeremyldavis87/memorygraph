# MemoryGraph Development Guide

This guide covers local development setup and multi-environment deployment for the MemoryGraph application.

## 🏗️ Architecture Overview

MemoryGraph uses a multi-environment architecture:

- **Local Development**: Run on your machine with Docker services
- **Dev Environment**: Deployed from `develop` branch to AWS
- **Prod Environment**: Deployed from `main` branch to AWS

## 🚀 Quick Start (Local Development)

### Prerequisites

- Docker and Docker Compose
- Node.js 18+
- Python 3.12+
- Git

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd memorygraph
   ```

2. **Run the setup script**:
   ```bash
   ./scripts/setup-local-dev.sh
   ```

3. **Configure environment variables**:
   - Update `backend/.env` with your API keys
   - Update `frontend/.env` if needed

4. **Start development environment**:
   ```bash
   ./start-dev.sh
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development Scripts

- `./start-dev.sh` - Start all development services
- `./stop-dev.sh` - Stop all development services
- `docker-compose up -d` - Start only Docker services (PostgreSQL, Redis)
- `docker-compose down` - Stop Docker services

## 🌍 Multi-Environment Deployment

### Environment Structure

```
infrastructure/
├── modules/           # Reusable Terraform modules
│   ├── vpc/          # VPC and networking
│   ├── security/     # Security groups
│   ├── database/     # RDS and ElastiCache
│   ├── ecs/          # ECS cluster and services
│   ├── alb/          # Application Load Balancer
│   └── ecr/          # ECR repositories
└── environments/
    ├── dev/          # Development environment
    └── prod/         # Production environment
```

### Branch Strategy

- **Feature branches** (`feature/*`, `cursor/*`): Local development only
- **`develop` branch**: Deploys to dev environment
- **`main` branch**: Deploys to prod environment

### Environment Differences

| Feature | Local | Dev | Prod |
|---------|-------|-----|------|
| Database | PostgreSQL (Docker) | RDS t3.micro | RDS t3.small |
| Redis | Redis (Docker) | ElastiCache t3.micro | ElastiCache t3.small |
| ECS Tasks | N/A | 1 task (256 CPU, 512 MB) | 3 tasks (1024 CPU, 2048 MB) |
| VPC | N/A | 2 AZs | 3 AZs with NAT Gateway |
| Log Retention | N/A | 3 days | 30 days |
| Image Retention | N/A | 5 images | 20 images |

## 🔧 Infrastructure Management

### Prerequisites for Infrastructure

- AWS CLI configured
- Terraform 1.6+
- Appropriate AWS permissions

### Deploy Infrastructure

#### Dev Environment

```bash
cd infrastructure/environments/dev
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

#### Prod Environment

```bash
cd infrastructure/environments/prod
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

### Required AWS Secrets

Set up the following secrets in GitHub:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DATABASE_PASSWORD_DEV`
- `DATABASE_PASSWORD_PROD`

### Required AWS Secrets Manager Secrets

Create the following secrets in AWS Secrets Manager:

#### Dev Environment
- `memorygraph/dev/jwt-secret`
- `memorygraph/dev/openai-api-key`
- `memorygraph/dev/anthropic-api-key`

#### Prod Environment
- `memorygraph/prod/jwt-secret`
- `memorygraph/prod/openai-api-key`
- `memorygraph/prod/anthropic-api-key`

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline automatically:

1. **Tests**: Runs on all branches
   - Python tests
   - Node.js tests
   - Frontend build

2. **Dev Deployment**: Runs on `develop` branch pushes
   - Builds and pushes Docker images to ECR
   - Deploys to ECS dev environment
   - Updates infrastructure if needed

3. **Prod Deployment**: Runs on `main` branch pushes
   - Builds and pushes Docker images to ECR
   - Deploys to ECS prod environment
   - Updates infrastructure if needed

### Manual Deployment

You can manually trigger deployments by pushing to the respective branches:

```bash
# Deploy to dev
git checkout develop
git push origin develop

# Deploy to prod
git checkout main
git push origin main
```

## 🔍 Monitoring and Debugging

### Local Development

- **Backend logs**: Check terminal where `uvicorn` is running
- **Frontend logs**: Check terminal where `npm start` is running
- **Database**: Connect to `localhost:5432` with credentials from `docker-compose.yml`
- **Redis**: Connect to `localhost:6379`

### AWS Environments

- **ECS Logs**: CloudWatch Logs groups `/ecs/memorygraph-{environment}`
- **ALB Logs**: Enable access logs in ALB configuration
- **RDS Logs**: CloudWatch Logs for database
- **ElastiCache**: CloudWatch metrics

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 8000, 5432, 6379 are available
2. **Docker issues**: Run `docker-compose down && docker-compose up -d`
3. **Permission issues**: Check file permissions on scripts
4. **API key issues**: Verify secrets are set correctly in AWS Secrets Manager

## 📁 Project Structure

```
memorygraph/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── .env               # Backend environment variables
├── frontend/               # React frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   ├── Dockerfile         # Frontend container
│   └── .env              # Frontend environment variables
├── infrastructure/         # Terraform infrastructure
│   ├── modules/           # Reusable modules
│   └── environments/      # Environment-specific configs
├── scripts/               # Development scripts
├── docker-compose.yml     # Local development services
├── start-dev.sh          # Start development environment
└── stop-dev.sh           # Stop development environment
```

## 🛠️ Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Develop locally**:
   ```bash
   ./start-dev.sh
   # Make your changes
   # Test locally
   ```

3. **Test changes**:
   ```bash
   # Backend tests
   cd backend && python -m pytest tests/ -v
   
   # Frontend tests
   cd frontend && npm test
   
   # Build test
   cd frontend && npm run build
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin feature/your-feature-name
   ```

5. **Create pull request** to `develop` for dev deployment or `main` for prod deployment

## 🔐 Security Considerations

- Never commit API keys or secrets to version control
- Use environment variables for all sensitive configuration
- Rotate secrets regularly
- Use different secrets for each environment
- Enable encryption at rest for databases
- Use HTTPS in production (configure ALB with SSL certificate)

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)