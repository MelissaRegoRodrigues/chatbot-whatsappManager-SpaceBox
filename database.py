import psycopg2
from dotenv import load_dotenv
import os

load_dotenv() 

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        port=os.environ.get('DB_PORT', 5432),
        database=os.environ.get('DB_NAME'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'))
    return conn

def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS auth_codes ('
                'phone_number VARCHAR(255) NOT NULL PRIMARY KEY,'
                'code VARCHAR(6) NOT NULL,'
                'created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP'
                ');')
    conn.commit()
    cur.close()
    conn.close()
