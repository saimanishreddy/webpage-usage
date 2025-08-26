#!/bin/bash

# Simple deployment script for the Flask web application
# This script handles the complete deployment process.

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S3_BUCKET="${1:-webapp-code-bucket-<name>}"
REGION="${2:-us-east-1}"
STACK_NAME="${3:-webapp-database-stack}"
KEY_PAIR="${4:-your-key-pair}"
DB_PASSWORD="${5}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

show_usage() {
    echo "Flask Web Application Deployment Script"
    echo "======================================"
    echo
    echo "Usage: $0 [S3_BUCKET] [REGION] [STACK_NAME] [KEY_PAIR] [DB_PASSWORD]"
    echo
    echo "Arguments:"
    echo "  S3_BUCKET    S3 bucket name (default: webapp-code-bucket-saiandru)"
    echo "  REGION       AWS region (default: us-east-1)"
    echo "  STACK_NAME   CloudFormation stack name (default: webapp-database-stack)"
    echo "  KEY_PAIR     EC2 Key Pair name (required)"
    echo "  DB_PASSWORD  Database password (required, 8+ characters)"
    echo
    echo "Examples:"
    echo "  $0 my-bucket us-east-1 my-stack my-keypair MySecurePass123"
    echo
    echo "Prerequisites:"
    echo "  - AWS CLI configured with appropriate permissions"
    echo "  - EC2 Key Pair created in target region"
    echo "  - Application code in ./app/ directory"
}

# Check if help is requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Validate required parameters
if [[ -z "$KEY_PAIR" ]]; then
    print_error "KEY_PAIR is required"
    show_usage
    exit 1
fi

if [[ -z "$DB_PASSWORD" ]]; then
    print_error "DB_PASSWORD is required"
    show_usage
    exit 1
fi

if [[ ${#DB_PASSWORD} -lt 8 ]]; then
    print_error "DB_PASSWORD must be at least 8 characters long"
    exit 1
fi

print_header "Flask Web Application Deployment"
print_status "Configuration:"
print_status "  S3 Bucket: $S3_BUCKET"
print_status "  Region: $REGION"
print_status "  Stack Name: $STACK_NAME"
print_status "  Key Pair: $KEY_PAIR"

# Step 1: Package and upload application code
print_header "Step 1: Package and Upload Application Code"
if [[ -f "$SCRIPT_DIR/deploy-app-to-s3.sh" ]]; then
    chmod +x "$SCRIPT_DIR/deploy-app-to-s3.sh"
    "$SCRIPT_DIR/deploy-app-to-s3.sh" "$S3_BUCKET" "$REGION" "$STACK_NAME"
else
    print_error "deploy-app-to-s3.sh not found"
    exit 1
fi

# Step 2: Deploy CloudFormation stack
print_header "Step 2: Deploy Infrastructure"
print_status "Creating CloudFormation stack..."

aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body file://"$SCRIPT_DIR/infrastructure/webapp-infrastructure.yaml" \
  --parameters \
    ParameterKey=KeyPairName,ParameterValue="$KEY_PAIR" \
    ParameterKey=DBPassword,ParameterValue="$DB_PASSWORD" \
    ParameterKey=AppCodeBucket,ParameterValue="$S3_BUCKET" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION"

print_status "Stack creation initiated. Monitoring progress..."

# Step 3: Monitor deployment
print_header "Step 3: Monitor Deployment"
print_status "Waiting for stack creation to complete..."

aws cloudformation wait stack-create-complete \
  --stack-name "$STACK_NAME" \
  --region "$REGION"

if [[ $? -eq 0 ]]; then
    print_status "Stack created successfully!"
else
    print_error "Stack creation failed!"
    print_status "Checking stack events for errors..."
    aws cloudformation describe-stack-events \
      --stack-name "$STACK_NAME" \
      --region "$REGION" \
      --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].[LogicalResourceId,ResourceStatusReason]' \
      --output table
    exit 1
fi

# Step 4: Get outputs
print_header "Step 4: Deployment Complete"
print_status "Getting stack outputs..."

APPLICATION_URL=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
  --output text)

EC2_IP=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --query 'Stacks[0].Outputs[?OutputKey==`EC2PublicIP`].OutputValue' \
  --output text)

print_header "Deployment Successful!"
echo
print_status "Application URL: $APPLICATION_URL"
print_status "EC2 Instance IP: $EC2_IP"
echo
print_status "You can now:"
print_status "1. Access your application at: $APPLICATION_URL"
print_status "2. SSH to EC2 instance: ssh -i $KEY_PAIR.pem ec2-user@$EC2_IP"
print_status "3. Check application logs: sudo journalctl -u webapp -f"
echo
print_warning "Note: It may take a few minutes for the application to be fully ready."
print_status "Check the health endpoint: $APPLICATION_URL/health"
