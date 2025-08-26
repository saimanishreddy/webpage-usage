"""
Database connection module using pymysql.
Handles database connections, operations, and error handling.
"""
import pymysql
import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager class for handling MySQL connections and operations."""
    
    def __init__(self, config=None):
        """Initialize database manager with configuration."""
        self.config = config or get_config()
        self.connection_config = self.config.get_database_config()
        self._connection = None
    
    def get_connection(self) -> pymysql.Connection:
        """Get database connection with error handling."""
        try:
            if self._connection is None or not self._connection.open:
                self._connection = pymysql.connect(**self.connection_config)
                logger.info("Database connection established")
            return self._connection
        except pymysql.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseConnectionError(f"Failed to connect to database: {e}")
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor with automatic cleanup."""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            yield cursor
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database operation error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
        except pymysql.Error as e:
            logger.error(f"Query execution error: {e}")
            raise DatabaseOperationError(f"Query execution failed: {e}")
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """Execute INSERT query and return last insert ID."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.lastrowid
        except pymysql.Error as e:
            logger.error(f"Insert operation error: {e}")
            raise DatabaseOperationError(f"Insert operation failed: {e}")
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute UPDATE query and return affected rows count."""
        try:
            with self.get_cursor() as cursor:
                affected_rows = cursor.execute(query, params)
                return affected_rows
        except pymysql.Error as e:
            logger.error(f"Update operation error: {e}")
            raise DatabaseOperationError(f"Update operation failed: {e}")
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def initialize_database(self):
        """Initialize database with required tables."""
        create_table_query = """
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
        
        try:
            with self.get_cursor() as cursor:
                cursor.execute(create_table_query)
                logger.info("Database tables initialized successfully")
        except pymysql.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise DatabaseOperationError(f"Database initialization failed: {e}")
    
    def close_connection(self):
        """Close database connection."""
        if self._connection and self._connection.open:
            self._connection.close()
            logger.info("Database connection closed")


class UserSubmissionRepository:
    """Repository class for user submission operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        """Initialize repository with database manager."""
        self.db_manager = db_manager
    
    def create_submission(self, name: str, email: str, message: str) -> int:
        """Create a new user submission."""
        query = """
        INSERT INTO user_submissions (name, email, message)
        VALUES (%s, %s, %s)
        """
        params = (name, email, message)
        
        try:
            submission_id = self.db_manager.execute_insert(query, params)
            logger.info(f"User submission created with ID: {submission_id}")
            return submission_id
        except Exception as e:
            logger.error(f"Failed to create user submission: {e}")
            raise
    
    def get_submission_by_id(self, submission_id: int) -> Optional[Dict[str, Any]]:
        """Get user submission by ID."""
        query = """
        SELECT id, name, email, message, created_at
        FROM user_submissions
        WHERE id = %s
        """
        params = (submission_id,)
        
        try:
            results = self.db_manager.execute_query(query, params)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Failed to get user submission: {e}")
            raise
    
    def get_all_submissions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all user submissions with optional limit."""
        query = """
        SELECT id, name, email, message, created_at
        FROM user_submissions
        ORDER BY created_at DESC
        LIMIT %s
        """
        params = (limit,)
        
        try:
            return self.db_manager.execute_query(query, params)
        except Exception as e:
            logger.error(f"Failed to get user submissions: {e}")
            raise


# Custom exceptions
class DatabaseConnectionError(Exception):
    """Exception raised for database connection errors."""
    pass


class DatabaseOperationError(Exception):
    """Exception raised for database operation errors."""
    pass


# Global database manager instance
db_manager = DatabaseManager()
user_submission_repo = UserSubmissionRepository(db_manager)