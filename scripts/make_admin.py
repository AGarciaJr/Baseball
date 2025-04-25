import os
import sys
import logging

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def make_user_admin(username):
    """Make a user an admin."""
    try:
        user = User.query.filter_by(username=username).first()
        if not user:
            logger.error(f"User '{username}' not found")
            return False
        
        user.is_admin = True
        db.session.commit()
        logger.info(f"Successfully made user '{username}' an admin")
        return True
            
    except Exception as e:
        logger.error(f"Error making user admin: {e}")
        return False

if __name__ == "__main__":
    with app.app_context():
        username = "Admin"  # Change this to the username you want to make admin
        success = make_user_admin(username)
        if success:
            logger.info("Operation completed successfully!")
        else:
            logger.error("Operation failed!") 