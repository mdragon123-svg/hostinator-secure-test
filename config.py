"""
Configuration management for Hostinator application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
    
    # Database Configuration
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_ROOT_USER'),
        'password': os.getenv('DB_ROOT_PASSWORD'),
        'database': 'hostinator_db',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
        'autocommit': True,
        'pool_name': 'hostinator_pool',
        'pool_size': 10,
        'pool_reset_session': True,
        'connect_timeout': int(os.getenv('MYSQL_CONNECT_TIMEOUT', '30')),
        'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
    }
    
    # Validate required database environment variables
    required_db_vars = ['DB_HOST', 'DB_ROOT_USER', 'DB_ROOT_PASSWORD']
    for var in required_db_vars:
        if not os.getenv(var):
            raise ValueError(f"Required environment variable {var} is not set")
    
    # SSH Configuration for backend machine
    SSH_CONFIG = {
        'hostname': os.getenv('SSH_HOSTNAME'),
        'port': int(os.getenv('SSH_PORT', '22')),
        'username': os.getenv('SSH_USERNAME'),
        'password': os.getenv('SSH_PASSWORD')
    }
    
    # Validate required SSH environment variables
    required_ssh_vars = ['SSH_HOSTNAME', 'SSH_USERNAME', 'SSH_PASSWORD']
    for var in required_ssh_vars:
        if not os.getenv(var):
            raise ValueError(f"Required environment variable {var} is not set")

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
