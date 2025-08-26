"""
Flask web application package.
"""
from .app import app, create_app
from .config import get_config
from .database import db_manager, user_submission_repo

__version__ = "1.0.0"
__all__ = ['app', 'create_app', 'get_config', 'db_manager', 'user_submission_repo']