from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_login():
    """Test the login functionality directly."""
    try:
        # First, delete any existing test user
        test_user = User.query.filter_by(username="testuser").first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
            logger.info("Deleted existing test user")
        
        # Create a new test user with a known password
        password = "testpassword123"
        test_user = User(username="testuser")
        test_user.set_password(password)
        
        db.session.add(test_user)
        db.session.commit()
        logger.info(f"Created test user with username: testuser")
        
        # Retrieve the user from the database
        retrieved_user = User.query.filter_by(username="testuser").first()
        if not retrieved_user:
            logger.error("Failed to retrieve the test user from the database")
            return False
        
        logger.info(f"Retrieved user: {retrieved_user.username}")
        
        # Test password verification
        is_valid = retrieved_user.check_password(password)
        logger.info(f"Password verification result: {is_valid}")
        
        # Test with wrong password
        is_invalid = retrieved_user.check_password("wrongpassword")
        logger.info(f"Wrong password verification result (should be False): {is_invalid}")
        
        return is_valid and not is_invalid
            
    except Exception as e:
        logger.error(f"Error testing login: {e}")
        return False

if __name__ == "__main__":
    with app.app_context():
        success = test_login()
        if success:
            logger.info("All login tests passed successfully!")
        else:
            logger.error("Login tests failed!") 