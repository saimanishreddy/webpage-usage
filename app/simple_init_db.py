#!/usr/bin/env python3
"""
Simple database initialization script.
Creates the user_submissions table if it doesn't exist.
"""
import os
import sys
import time
import pymysql
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with retry logic."""
    # Database configuration from environment variables
    db_config = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', '3306')),
        'user': os.environ.get('DB_USER', 'webappuser'),
        'password': os.environ.get('DB_PASSWORD', 'webapp_password'),
        'database': os.environ.get('DB_NAME', 'webapp_db'),
        'charset': 'utf8mb4'
    }
    
    logger.info(f"Connecting to database: {db_config['host']}:{db_config['port']}")
    logger.info(f"Database: {db_config['database']}, User: {db_config['user']}")
    
    # Retry logic for database connection
    max_retries = 10
    retry_delay = 30
    
    for attempt in range(max_retries):
        try:
            # Connect to database
            connection = pymysql.connect(**db_config)
            logger.info("Database connection successful!")
            
            # Create table
            with connection.cursor() as cursor:
                # Check MySQL version
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                logger.info(f"MySQL Version: {version[0]}")
                
                # Create table if not exists
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS user_submissions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_created_at (created_at),
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                
                cursor.execute(create_table_sql)
                connection.commit()
                logger.info("Table 'user_submissions' created successfully!")
                
                # Verify table exists
                cursor.execute("SHOW TABLES LIKE 'user_submissions'")
                result = cursor.fetchone()
                if result:
                    logger.info("Table verification successful")
                    # Show table structure
                    cursor.execute("DESCRIBE user_submissions")
                    columns = cursor.fetchall()
                    logger.info("Table structure:")
                    for column in columns:
                        logger.info(f"  {column[0]}: {column[1]}")
                else:
                    logger.error("Table verification failed")
                    return False
            
            connection.close()
            logger.info("Database initialization completed successfully!")
            return True
            
        except Exception as e:
            attempt_num = attempt + 1
            logger.error(f"Database connection attempt {attempt_num}/{max_retries} failed: {e}")
            
            if attempt_num < max_retries:
                logger.info(f"Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                logger.error("All database connection attempts failed!")
                return False
    
    return False

if __name__ == '__main__':
    logger.info("Starting database initialization...")
    success = init_database()
    
    if success:
        logger.info("Database initialization completed successfully!")
        sys.exit(0)
    else:
        logger.error("Database initialization failed!")
        sys.exit(1)
