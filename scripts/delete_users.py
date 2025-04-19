from app import app, db, User
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def delete_users():
    """Delete all users from the database."""
    try:
        # Get all users
        users = User.query.all()
        
        if not users:
            logger.info("No users found in the database.")
            return
        
        # Delete all users
        for user in users:
            db.session.delete(user)
            logger.info(f"Deleted user: {user.username}")
        
        # Commit changes
        db.session.commit()
        logger.info("All users have been deleted successfully.")
            
    except Exception as e:
        logger.error(f"Error deleting users: {e}")

if __name__ == "__main__":
    with app.app_context():
        delete_users() 