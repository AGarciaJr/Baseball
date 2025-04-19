from app import app, db, User
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_database():
    """Check the contents of the database."""
    try:
        # Get all users
        users = User.query.all()
        
        if not users:
            logger.info("No users found in the database.")
            return
        
        logger.info(f"Found {len(users)} users in the database:")
        for user in users:
            logger.info(f"User ID: {user.id}")
            logger.info(f"Username: {user.username}")
            logger.info(f"Password Hash: {user.password_hash[:20]}...")
            logger.info(f"Is Admin: {user.is_admin}")
            logger.info(f"Is Banned: {user.is_banned}")
            logger.info(f"Score: {user.score}")
            logger.info("-" * 30)
            
    except Exception as e:
        logger.error(f"Error checking database: {e}")

if __name__ == "__main__":
    with app.app_context():
        check_database() 