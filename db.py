from csi3335f2024 import mysql as db_config
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host=db_config['location'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        charset='utf8mb4',
        collation='utf8mb4_general_ci'
    )

def award_achievement(user_id, name, description, image_path=None):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT IGNORE INTO achievements (user_id, name, description, image_path)
            VALUES (%s, %s, %s, %s)
        """, (user_id, name, description, image_path))
        conn.commit()
        return cur.rowcount > 0  # True if inserted
    except Exception as e:
        print("Achievement error:", e)
        return False
    finally:
        cur.close()
        conn.close()
