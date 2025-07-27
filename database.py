import psycopg2
import os

def get_db_connection():
    conn = psycopg2.connect(
        host="db-postgres-spacebox",
        database="postgres",
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
