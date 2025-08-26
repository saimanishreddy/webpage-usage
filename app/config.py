"""
Configuration module for database and application settings.
Handles environment variables and database connection parameters.
"""
import os
from typing import Optional


class Config:
    """Application configuration class."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', '3306'))
    DB_NAME = os.environ.get('DB_NAME', 'webapp_db')
    DB_USER = os.environ.get('DB_USER', 'webappuser')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'webapp_password')
    
    # Connection pool settings
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', '5'))
    DB_POOL_RECYCLE = int(os.environ.get('DB_POOL_RECYCLE', '3600'))
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database connection URL."""
        return f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_database_config(cls) -> dict:
        """Get database configuration as dictionary."""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'charset': 'utf8mb4',
            'autocommit': True
        }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'webapp_dev_db')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    @classmethod
    def validate(cls):
        """Validate production configuration."""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        if not cls.DB_PASSWORD:
            raise ValueError("DB_PASSWORD environment variable must be set in production")


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration object based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])
