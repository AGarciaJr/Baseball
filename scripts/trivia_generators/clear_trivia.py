import mysql.connector
import logging
import getpass

logging.basicConfig(level=logging.INFO)

# Prompt for the MySQL root password
password = getpass.getpass("Enter your MySQL root password: ")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=password,
        database="Sandlot2TheSQL"
    )
    cursor = conn.cursor()

    # Disable foreign key checks temporarily
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

    # Truncate child then parent to avoid FK errors and reset AUTO_INCREMENT
    cursor.execute("TRUNCATE TABLE trivia_answers;")
    cursor.execute("TRUNCATE TABLE trivia_questions;")

    # Re-enable foreign key checks
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    conn.commit()
    logging.info("✅ All trivia questions and answers have been cleared and auto-increment counters reset.")

except mysql.connector.Error as err:
    logging.error(f"❌ Error: {err}")
    conn.rollback()

finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
