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