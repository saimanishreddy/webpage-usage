#!/bin/bash

# Script to package and upload application code to S3
# This should be run before deploying the CloudFormation stack.

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"
S3_BUCKET="${1:-webapp-code-bucket}"
REGION="${2:-us-east-1}"
STACK_NAME="${3:-webapp-database-stack}"

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
    echo -e "${BLUE}$1${NC}"
}

# Function to show usage
show_usage() {
    echo "Application Code Deployment Script"
    echo "================================="
    echo
    echo "Usage: $0 [S3_BUCKET] [REGION] [STACK_NAME]"
    echo
    echo "Arguments:"
    echo "  S3_BUCKET    S3 bucket name (default: webapp-code-bucket-saiandru)"
    echo "  REGION       AWS region (default: us-east-1)"
    echo "  STACK_NAME   CloudFormation stack name (default: webapp-code-bucket-saiandru)"
    echo
    echo "Examples:"
    echo "  $0                                    # Use defaults"
    echo "  $0 my-app-bucket                      # Custom bucket"
    echo "  $0 my-app-bucket us-west-2            # Custom bucket and region"
    echo "  $0 my-app-bucket us-west-2 my-stack   # All custom"
}

# Check if help is requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

print_header "=== Application Code Deployment ==="

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    print_error "App directory not found: $APP_DIR"
    exit 1
fi

# Check if required files exist
required_files=("app.py" "requirements.txt" "templates/index.html" "static/css/style.css")
for file in "${required_files[@]}"; do
    if [ ! -f "$APP_DIR/$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    fi
done

print_status "App directory structure validated"

# Create temporary directory for packaging
TEMP_DIR=$(mktemp -d)
PACKAGE_DIR="$TEMP_DIR/webapp"

print_status "Creating package in temporary directory: $TEMP_DIR"

# Copy application files
mkdir -p "$PACKAGE_DIR"
cp -r "$APP_DIR"/* "$PACKAGE_DIR/"

# Remove unnecessary files
cd "$PACKAGE_DIR"
rm -rf __pycache__ .venv .git .kiro

print_status "Application files packaged successfully"

# Create ZIP file
cd "$TEMP_DIR"
zip -r webapp.zip webapp/

print_status "ZIP package created: webapp.zip"

# Check if S3 bucket exists, create if it doesn't
if ! aws s3 ls "s3://$S3_BUCKET" --region "$REGION" >/dev/null 2>&1; then
    print_warning "S3 bucket '$S3_BUCKET' does not exist. Creating..."
    aws s3 mb "s3://$S3_BUCKET" --region "$REGION"
    print_status "S3 bucket created: $S3_BUCKET"
else
    print_status "S3 bucket exists: $S3_BUCKET"
fi

# Upload to S3
print_status "Uploading application package to S3..."
aws s3 cp webapp.zip "s3://$S3_BUCKET/webapp.zip" --region "$REGION"

print_status "Application code uploaded successfully to s3://$S3_BUCKET/webapp.zip"

# Clean up temporary files
rm -rf "$TEMP_DIR"

print_status "Temporary files cleaned up"

print_header "=== Deployment Instructions ==="
echo
echo "Now deploy your infrastructure using:"
echo
echo "aws cloudformation create-stack \\"
echo "  --stack-name $STACK_NAME \\"
echo "  --template-body file://infrastructure/webapp-infrastructure.yaml \\"
echo "  --parameters ParameterKey=AppCodeBucket,ParameterValue=$S3_BUCKET \\"
echo "  --capabilities CAPABILITY_IAM \\"
echo "  --region $REGION"
echo
echo "Or use the deploy script:"
echo "  ./deploy.sh infrastructure --bucket $S3_BUCKET"
echo

print_header "=== Next Steps ==="
echo "1. Deploy the CloudFormation infrastructure stack"
echo "2. The EC2 instance will automatically download and deploy your app code"
echo "3. Monitor the stack creation progress"
echo "4. Access your application through the Application Load Balancer"
