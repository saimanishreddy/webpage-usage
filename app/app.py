"""
Main Flask application file with basic route structure.
Handles HTTP requests, form processing, and database operations.
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import logging
import os
from database import db_manager, user_submission_repo, DatabaseConnectionError, DatabaseOperationError
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)

# Initialize database on startup
try:
    db_manager.initialize_database()
    logger.info("Application started successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")


@app.route('/', methods=['GET', 'POST'])
def index():
    """Display the main form page and handle form submission."""
    if request.method == 'GET':
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f"Error rendering index page: {e}")
            return render_template('error.html', error="Failed to load the form page"), 500
    
    elif request.method == 'POST':
        return submit_form()
def submit_form():
    """Handle form submission and store data in database."""
    try:
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate form data
        validation_errors = validate_form_data(name, email, message)
        if validation_errors:
            for error in validation_errors:
                flash(error, 'error')
            return render_template('index.html'), 400
        
        # Save to database
        submission_id = user_submission_repo.create_submission(name, email, message)
        
        logger.info(f"Form submitted successfully - ID: {submission_id}, Name: {name}, Email: {email}")
        flash('Thank you! Your submission has been received successfully.', 'success')
        
        return render_template('success.html', submission_id=submission_id)
        
    except DatabaseConnectionError as e:
        logger.error(f"Database connection error during form submission: {e}")
        flash('Sorry, we are experiencing technical difficulties. Please try again later.', 'error')
        return render_template('index.html'), 503
        
    except DatabaseOperationError as e:
        logger.error(f"Database operation error during form submission: {e}")
        flash('Sorry, we could not process your submission. Please try again.', 'error')
        return render_template('index.html'), 500
        
    except Exception as e:
        logger.error(f"Unexpected error during form submission: {e}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return render_template('index.html'), 500


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        is_db_healthy = db_manager.test_connection()
        
        health_status = {
            'status': 'healthy' if is_db_healthy else 'unhealthy',
            'database': 'connected' if is_db_healthy else 'disconnected'
        }
        
        status_code = 200 if is_db_healthy else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'database': 'error'
        }), 503
@app.route('/submissions')
def view_submissions():
    """View all submissions (for debugging/admin purposes)."""
    try:
        # Only allow in development mode
        if not app.config.get('DEBUG', False):
            return "Access denied", 403
        
        submissions = user_submission_repo.get_all_submissions(limit=50)
        return render_template('submissions.html', submissions=submissions)
        
    except Exception as e:
        logger.error(f"Error retrieving submissions: {e}")
        return jsonify({'error': 'Failed to retrieve submissions'}), 500


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html', error="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', error="Internal server error"), 500


def validate_form_data(name: str, email: str, message: str) -> list:
    """Validate form input data."""
    errors = []
    
    # Validate name
    if not name:
        errors.append("Name is required.")
    elif len(name) > 100:
        errors.append("Name must be less than 100 characters.")
    
    # Validate email
    if not email:
        errors.append("Email is required.")
    elif len(email) > 100:
        errors.append("Email must be less than 100 characters.")
    elif '@' not in email or '.' not in email.split('@')[-1]:
        errors.append("Please enter a valid email address.")
    
    # Validate message (optional but with length limit)
    if message and len(message) > 1000:
        errors.append("Message must be less than 1000 characters.")
    
    return errors


def create_app(config_name=None):
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    config_obj = get_config(config_name)
    app.config.from_object(config_obj)
    
    # Validate production configuration
    if config_name == 'production':
        config_obj.validate()
    
    return app


if __name__ == '__main__':
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting Flask application in {config_name} mode on {host}:{port}")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=app.config.get('DEBUG', False)
    )
