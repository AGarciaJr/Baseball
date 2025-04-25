import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_connection():
    """Check the database connection."""
    try:
        import pymysql
        import pymysql.cursors
        
        # Get connection details from environment
        db_url = os.getenv('DATABASE_URL', 'mysql://root:password@localhost/Sandlot2TheSQL')
        
        # Parse the URL
        # Format: mysql://username:password@host/database
        parts = db_url.split('://')[1].split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')
        
        username = user_pass[0]
        password = user_pass[1]
        host = host_db[0]
        database = host_db[1]
        
        logger.info(f"Attempting to connect to MySQL with:")
        logger.info(f"Host: {host}")
        logger.info(f"Database: {database}")
        logger.info(f"Username: {username}")
        
        # Try to connect
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        logger.info("Successfully connected to MySQL!")
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return False

if __name__ == "__main__":
    success = check_connection()
    if success:
        logger.info("Database connection test passed!")
    else:
        logger.error("Database connection test failed!") 