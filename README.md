# Flask Web Application on AWS

A simple Flask web application that collects user input and stores it in a MySQL database, deployed on AWS using CloudFormation.

## Quick Deployment

### Prerequisites
- AWS CLI configured
- EC2 Key Pair created in your region

### Deploy in One Command
```bash
./deploy.sh webapp-code-bucket-saiandru us-east-1 webapp-stack YOUR_KEY_PAIR_NAME YourSecurePass123
```

### Manual Steps
1. **Upload app code:**
   ```bash
   ./deploy-app-to-s3.sh
   ```

2. **Deploy infrastructure:**
   ```bash
   aws cloudformation create-stack \
     --stack-name webapp-database-stack \
     --template-body file://infrastructure/webapp-infrastructure.yaml \
     --parameters \
       ParameterKey=KeyPairName,ParameterValue=YOUR_KEY_PAIR_NAME \
       ParameterKey=DBPassword,ParameterValue=YourSecurePass123 \
       ParameterKey=AppCodeBucket,ParameterValue=webapp-code-bucket-saiandru \
     --capabilities CAPABILITY_IAM \
     --region us-east-1
   ```

3. **Get application URL:**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name webapp-database-stack \
     --region us-east-1 \
     --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
     --output text
   ```

## What Gets Deployed
- **VPC** with public/private subnets
- **EC2** instance running Flask app
- **RDS MySQL** database
- **Application Load Balancer**
- **Security Groups** and **IAM roles**

## Project Structure
```
├── app/                          # Flask application
│   ├── app.py                   # Main application
│   ├── database.py              # Database operations
│   ├── simple_init_db.py        # Database initialization
│   ├── requirements.txt         # Dependencies
│   └── webapp.service           # Systemd service
├── infrastructure/
│   └── webapp-infrastructure.yaml # CloudFormation template
├── deploy-app-to-s3.sh         # Upload app to S3
└── deploy.sh                    # Complete deployment script
```

## Troubleshooting

**SSH to EC2:**
```bash
ssh -i YOUR_KEY_PAIR.pem ec2-user@EC2_PUBLIC_IP
```

**Check service:**
```bash
sudo systemctl status webapp
sudo journalctl -u webapp -f
```

**Check setup logs:**
```bash
sudo tail -f /var/log/webapp-setup.log
```

## Cleanup
```bash
aws cloudformation delete-stack --stack-name webapp-database-stack --region us-east-1
aws s3 rb s3://webapp-code-bucket-saiandru --force
```

## Architecture
```
Internet → Load Balancer → EC2 (Flask) → RDS MySQL
```

The application runs on EC2 with a uv virtual environment, connects to RDS MySQL in private subnets, and is accessible through an Application Load Balancer.
