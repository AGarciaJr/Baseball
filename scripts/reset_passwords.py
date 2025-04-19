from app import app, db, User
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def reset_passwords():
    """Reset passwords for all users to a known value."""
    try:
        # Get all users
        users = User.query.all()
        
        if not users:
            logger.info("No users found in the database.")
            return
        
        # New password for all users
        new_password = "password123"
        
        for user in users:
            # Reset password
            user.set_password(new_password)
            logger.info(f"Reset password for user: {user.username}")
        
        # Commit changes
        db.session.commit()
        logger.info("All passwords have been reset successfully.")
        logger.info(f"New password for all users: {new_password}")
            
    except Exception as e:
        logger.error(f"Error resetting passwords: {e}")

if __name__ == "__main__":
    with app.app_context():
        reset_passwords() 