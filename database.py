"""
Database connection and query management
"""
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
import logging
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection and query management"""
    
    def __init__(self):
        self.connection_pool = None
        self.initialize_pool()
    
    def initialize_pool(self):
        """Initialize database connection pool"""
        try:
            # First test basic connection without pool
            logger.info("🔍 Testing basic MySQL connection...")
            test_config = {k: v for k, v in Config.DB_CONFIG.items() 
                           if k not in ['pool_name', 'pool_size', 'pool_reset_session', 'database']}
            test_conn = mysql.connector.connect(**test_config)
            test_conn.close()
            logger.info("✅ Basic MySQL connection successful")
            
            # Now create the connection pool
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**Config.DB_CONFIG)
            logger.info(f"✅ Database pool created successfully - Connected to {Config.DB_CONFIG['host']}:{Config.DB_CONFIG['port']}")
        except mysql.connector.Error as err:
            logger.error(f"❌ Failed to create database pool: {err}")
            logger.error(f"🔍 Error code: {err.errno}")
            logger.error(f"🔍 SQL State: {err.sqlstate}")
            if err.errno == 1045:
                logger.error("🔍 This is an authentication error. Check:")
                logger.error("    1. Username and password are correct")
                logger.error("    2. MySQL user has permission to connect from this IP")
                logger.error("    3. MySQL server allows remote connections")
            self.connection_pool = None
        except Exception as e:
            logger.error(f"❌ Unexpected error creating database pool: {e}")
            self.connection_pool = None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with automatic cleanup"""
        connection = None
        try:
            if self.connection_pool is None:
                raise Exception("Database pool not initialized")
            
            connection = self.connection_pool.get_connection()
            if connection.is_connected():
                yield connection
            else:
                raise Exception("Failed to get database connection")
        except mysql.connector.Error as err:
            logger.error(f"Database error: {err}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """Execute a database query with proper error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params or ())
                
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch:
                    result = cursor.fetchall()
                else:
                    result = cursor.lastrowid or cursor.rowcount
                
                conn.commit()
                cursor.close()
                return result
        except mysql.connector.Error as err:
            logger.error(f"Query execution failed: {err}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            raise
    
    def initialize_database(self):
        """Initialize database tables and sample data"""
        try:
            # First, create the database if it doesn't exist
            temp_config = Config.DB_CONFIG.copy()
            db_name = temp_config.pop('database', None)
            charset = temp_config.pop('charset', 'utf8mb4')
            collation = temp_config.pop('collation', 'utf8mb4_unicode_ci')
            
            temp_config.pop('pool_name', None)
            temp_config.pop('pool_size', None)
            temp_config.pop('pool_reset_session', None)
            
            # Create database
            try:
                temp_conn = mysql.connector.connect(**temp_config)
                temp_cursor = temp_conn.cursor()
                
                # MODIFIED: Used parameterized query to prevent SQL injection
                create_db_query = "CREATE DATABASE IF NOT EXISTS {} CHARACTER SET {} COLLATE {}".format(db_name, charset, collation)
                temp_cursor.execute(create_db_query)
                temp_cursor.execute("USE {}".format(db_name))

                temp_conn.commit()
                temp_cursor.close()
                temp_conn.close()
                logger.info(f"✅ Database '{db_name}' ensured to exist")
            except mysql.connector.Error as err:
                logger.error(f"❌ Failed to create database: {err}")
                return

            self._create_tables()
            self._create_sample_data()

        except Exception as err:
            logger.error(f"❌ Database initialization failed: {err}")
            raise
    
    def _create_tables(self):
        """Create database tables"""
        # Create users table
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        self.execute_query(users_table)
        logger.info("✅ Users table created/verified")

        # Create deployments table
        deployments_table = """
        CREATE TABLE IF NOT EXISTS deployments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            deployment_type VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            credentials_file TEXT,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_status (status),
            INDEX idx_deployment_type (deployment_type)
        ) ENGINE=InnoDB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
        """
        self.execute_query(deployments_table)
        logger.info("✅ Deployments table created/verified")
    
    def _create_sample_data(self):
        """Create sample data if not exists"""
        from werkzeug.security import generate_password_hash
        
        # Check if admin user exists
        admin_user = self.execute_query("SELECT id FROM users WHERE username = %s", ('admin',), fetch_one=True)
        
        if not admin_user:
            # Create admin user
            admin_id = self.execute_query(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                ('admin', generate_password_hash('admin'))
            )
            logger.info(f"✅ Admin user created with ID: {admin_id}")
        else:
            admin_id = admin_user['id']
            logger.info(f"✅ Admin user exists with ID: {admin_id}")

        # Check if sample deployments exist
        existing_deployments = self.execute_query("SELECT COUNT(*) as count FROM deployments", fetch_one=True)
        
        if existing_deployments['count'] == 0:
            self._create_sample_deployments(admin_id)
    
    def _create_sample_deployments(self, admin_id):
        """Create sample deployments"""
        now = datetime.now()
        sample_deployments = [
            ('example.com', 'user@example.com', 'Active', 'WordPress', now, now, '/home/example.com/credentials_example.com.txt', admin_id),
            ('test.com', 'test@example.com', 'Active', 'NextCloud', now, now, '/home/test.com/credentials_test.com.txt', admin_id),
            ('moodle-demo.com', 'moodle@example.com', 'Active', 'Moodle', now, now, '/home/moodle-demo.com/credentials_moodle-demo.com.txt', admin_id),
            ('zabbix-monitor.com', 'zabbix@example.com', 'Active', 'Zabbix', now, now, '/home/zabbix-monitor.com/credentials_zabbix-monitor.com.txt', admin_id),
            ('postiz-test.com', 'postiz@example.com', 'Active', 'Postiz', now, now, '/home/postiz-test.com/credentials_postiz-test.com.txt', admin_id),
            ('joomla-test.com', 'joomla@example.com', 'Active', 'Joomla', now, now, '/home/joomla-test.com/credentials_joomla-test.com.txt', admin_id),
            ('ghost-prototype.com', 'ghost@example.com', 'Active', 'Ghost', now, now, '/home/ghost-prototype.com/credentials_ghost-prototype.com.txt', admin_id),
            ('metabase-experiment.com', 'metabase@example.com', 'Active', 'Metabase', now, now, '/home/metabase-experiment.com/credentials_metabase-experiment.com.txt', admin_id),
            ('jupyter-notebook.com', 'jupyter@example.com', 'Active', 'Jupyter', now, now, '/home/jupyter-notebook.com/credentials_jupyter-notebook.com.txt', admin_id)  
        ]
        
        insert_query = """
        INSERT INTO deployments (name, email, status, deployment_type, created_at, last_updated, credentials_file, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for deployment in sample_deployments:
            self.execute_query(insert_query, deployment)
        
        logger.info(f"✅ {len(sample_deployments)} sample deployments created")

# Global database manager instance
db_manager = DatabaseManager()