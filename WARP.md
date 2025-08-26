# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is a Flask web application with AWS infrastructure deployment automation. The project implements a simple user submission form that stores data in a MySQL database, designed for deployment on AWS using CloudFormation with proper VPC, security, and auto-scaling considerations.

## Common Development Commands

### Local Development
```bash
# Set up Python virtual environment using uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv .venv --python 3.11
source .venv/bin/activate

# Install dependencies
uv pip install -r app/requirements.txt

# Run application locally
cd app
python app.py

# Run database initialization script
python simple_init_db.py

# Test health endpoint
curl http://localhost:5000/health
```

### AWS Deployment
```bash
# Complete deployment (recommended)
./deploy.sh webapp-code-bucket-saiandru us-east-1 webapp-stack YOUR_KEY_PAIR_NAME YourSecurePass123

# Manual deployment - upload app code first
./deploy-app-to-s3.sh webapp-code-bucket-saiandru us-east-1 webapp-stack

# Manual deployment - deploy infrastructure
aws cloudformation create-stack \
  --stack-name webapp-database-stack \
  --template-body file://infrastructure/webapp-infrastructure.yaml \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue=YOUR_KEY_PAIR_NAME \
    ParameterKey=DBPassword,ParameterValue=YourSecurePass123 \
    ParameterKey=AppCodeBucket,ParameterValue=webapp-code-bucket-saiandru \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# Get application URL after deployment
aws cloudformation describe-stacks \
  --stack-name webapp-database-stack \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
  --output text

# Cleanup resources
aws cloudformation delete-stack --stack-name webapp-database-stack --region us-east-1
aws s3 rb s3://webapp-code-bucket-saiandru --force
```

### Debugging and Troubleshooting
```bash
# SSH to EC2 instance for debugging
ssh -i YOUR_KEY_PAIR.pem ec2-user@EC2_PUBLIC_IP

# Check application service status
sudo systemctl status webapp
sudo journalctl -u webapp -f

# View setup logs
sudo tail -f /var/log/webapp-setup.log

# Test database connectivity from EC2
mysql -h DATABASE_ENDPOINT -u webappuser -p webapp_db
```

## Architecture Overview

The application follows a 3-tier architecture deployed on AWS:

### Application Layer
- **Flask Application** (`app/app.py`): Main web server with form handling, validation, and error management
- **Database Layer** (`app/database.py`): Repository pattern with connection pooling and custom exception handling
- **Configuration Management** (`app/config.py`): Environment-based configuration with development/production settings

### Infrastructure Layer (CloudFormation)
- **VPC**: Custom VPC with public/private subnets across 2 AZs for high availability
- **Security**: Multi-layered security groups (ALB → EC2 → RDS) with least privilege access
- **Compute**: EC2 instance with IAM roles for AWS service access, deployed with systemd service management
- **Database**: RDS MySQL in private subnets with automated backups and encryption
- **Load Balancing**: Application Load Balancer with health checks and auto-target registration

### Key Design Patterns

**Repository Pattern**: Database operations are abstracted through `UserSubmissionRepository` class, making database interactions testable and maintainable.

**Configuration Management**: Environment-specific configurations with validation for production deployments.

**Error Handling**: Comprehensive exception hierarchy with `DatabaseConnectionError` and `DatabaseOperationError` for proper error categorization.

**Infrastructure as Code**: Complete AWS infrastructure defined in CloudFormation with parameterized deployments.

## File Structure Understanding

```
├── app/                          # Flask application
│   ├── app.py                   # Main Flask app with routes and error handling
│   ├── database.py              # Database layer with repository pattern
│   ├── config.py                # Environment-based configuration
│   ├── simple_init_db.py        # Database initialization with retry logic
│   ├── requirements.txt         # Python dependencies
│   ├── webapp.service           # Systemd service configuration
│   ├── templates/               # Jinja2 HTML templates
│   └── static/                  # CSS/JS assets
├── infrastructure/
│   └── webapp-infrastructure.yaml # Complete AWS infrastructure definition
├── deploy-app-to-s3.sh         # Application packaging and S3 upload
└── deploy.sh                    # End-to-end deployment orchestration
```

## Environment Configuration

The application uses different configuration classes:
- `DevelopmentConfig`: Local development with debug mode
- `ProductionConfig`: AWS deployment with security validations

Key environment variables:
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: Database connection
- `SECRET_KEY`: Flask session security (auto-generated in production)
- `FLASK_ENV`: Determines configuration class loading

## Development Workflow

1. **Local Setup**: Use `uv` package manager for consistent Python environment management
2. **Database Testing**: Run `simple_init_db.py` to test database connectivity and schema creation
3. **Application Testing**: Use `/health` endpoint to verify app and database connectivity
4. **Deployment**: Use `deploy.sh` for complete infrastructure deployment or manual steps for debugging
5. **Monitoring**: Check CloudFormation stack events and EC2 instance logs for deployment issues

## AWS Infrastructure Notes

- **Networking**: Uses custom VPC with 10.0.0.0/16 CIDR, public subnets for ALB/EC2, private for RDS
- **Security**: Security groups implement defense in depth (ALB→EC2→RDS communication only)
- **Deployment**: EC2 User Data handles complete application setup including uv installation and systemd service configuration
- **Monitoring**: CloudWatch logs integration through systemd journal forwarding

## Database Schema

The application uses a single table `user_submissions`:
- `id`: Auto-increment primary key
- `name`: VARCHAR(100) - User's name
- `email`: VARCHAR(100) - User's email with basic validation
- `message`: TEXT - Optional user message
- `created_at`: Timestamp with automatic creation time
- Indexed on `created_at` and `email` for query performance
