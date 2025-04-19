import mysql.connector
import os
from dotenv import load_dotenv
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def replace_collation(sql_content):
    """Replace unsupported collation with a supported one."""
    return sql_content.replace('utf8mb4_0900_ai_ci', 'utf8mb4_general_ci')

def import_schema():
    """
    Import the baseball.sql schema into the Sandlot2TheSQL database
    """
    try:
        # Load environment variables from the correct path
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)
        
        # Get database credentials from environment variables
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        if not db_user or not db_password:
            logger.error("Database credentials not found in .env file")
            logger.error(f"DB_USER: {db_user}")
            logger.error(f"DB_PASSWORD: {'*' * len(db_password) if db_password else 'None'}")
            sys.exit(1)
        
        db_config = {
            'host': 'localhost',
            'user': db_user,
            'password': db_password,
            'database': 'Sandlot2TheSQL',
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_general_ci'
        }
        
        # Connect to MySQL
        logger.info("Connecting to MySQL...")
        logger.info(f"Using user: {db_user}")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Read the SQL file
        logger.info("Reading baseball.sql...")
        sql_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'baseball.sql')
        
        if not os.path.exists(sql_file_path):
            logger.error(f"baseball.sql not found at: {sql_file_path}")
            sys.exit(1)
            
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Replace problematic collation
        sql_content = replace_collation(sql_content)
        
        # Split the commands more intelligently
        commands = []
        current_command = []
        in_create_table = False
        in_insert = False
        
        for line in sql_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
                
            if line.upper().startswith('CREATE TABLE'):
                in_create_table = True
                current_command = [line]
            elif in_create_table and line.endswith(';'):
                current_command.append(line)
                commands.append(' '.join(current_command))
                current_command = []
                in_create_table = False
            elif in_create_table:
                current_command.append(line)
            elif line.upper().startswith('INSERT'):
                in_insert = True
                current_command = [line]
            elif in_insert and line.endswith(';'):
                current_command.append(line)
                commands.append(' '.join(current_command))
                current_command = []
                in_insert = False
            elif in_insert:
                current_command.append(line)
            elif line.endswith(';'):
                commands.append(line)
        
        # Execute each command
        logger.info("Executing SQL commands...")
        for command in commands:
            if command.strip():
                try:
                    cursor.execute(command)
                    conn.commit()
                except mysql.connector.Error as err:
                    logger.error(f"Error executing command: {err}")
                    logger.error(f"Failed command: {command[:200]}...")  # Log first 200 chars of failed command
        
        logger.info("Schema import completed successfully!")
        
    except mysql.connector.Error as err:
        logger.error(f"MySQL Error: {err}")
        if err.errno == 1045:  # Access denied
            logger.error("Access denied. Please check your database credentials in the .env file.")
        elif err.errno == 1049:  # Unknown database
            logger.error("Database 'Sandlot2TheSQL' does not exist. Please create it first.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error importing schema: {e}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_schema() 