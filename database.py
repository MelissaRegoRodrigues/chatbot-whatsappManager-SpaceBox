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

def upsert_auth_code(phone_number: str, auth_code: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO "AuthCode" ("phoneNumber", "code") VALUES (%s, %s) ON CONFLICT ("phoneNumber") DO UPDATE SET "code" = %s',
        (phone_number, auth_code, auth_code)
    )
    conn.commit()
    cur.close()
    conn.close()
