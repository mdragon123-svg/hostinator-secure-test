"""
Main Flask application entry point
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from mysql.connector import pooling
import os
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import paramiko
import io
from contextlib import contextmanager
import logging
from dotenv import load_dotenv
from config import Config
from database import db_manager

# Import blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.marketplace import marketplace_bp
from routes.deployments import deployments_bp
from routes.health import health_bp

# Load environment variables from .env file
load_dotenv()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(deployments_bp)
    app.register_blueprint(health_bp)
    
    # Initialize database
    try:
        db_manager.initialize_database()
        logger.info("🚀 Application initialized successfully")
        logger.info(f"📊 Database: {Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}/{Config.DB_CONFIG['database']}")
        logger.info(f"🔐 SSH Backend: {Config.SSH_CONFIG['hostname']}:{Config.SSH_CONFIG['port']}")
    except Exception as e:
        logger.error(f"❌ Application initialization failed: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting Hostinator with Remote MySQL Database")
    print(f"📊 Database: {Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}")
    print(f"🔐 Backend: {Config.SSH_CONFIG['hostname']}:{Config.SSH_CONFIG['port']}")
    print(f"🌐 App URL: http://localhost:5000")
    print(f"❤️  Health Check: http://localhost:5000/health")
    app.run(debug=False, host='0.0.0.0', port=5001)
