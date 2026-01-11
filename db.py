import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            port=os.getenv('DB_PORT')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# --- User Management (Same as before) ---
def get_user_by_name(user_name):
    conn = get_db_connection()
    if not conn: return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM public.users WHERE user_name = %s", (user_name,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

def create_user(user_id, user_name):
    conn = get_db_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO public.users (user_id, user_name) VALUES (%s, %s)", (user_id, user_name))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False

# --- Stash Management ---
def save_stash(url_id, user_id, url, summary, tags):
    conn = get_db_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO public.stashed_urls (url_id, user_id, url, summary, tags) VALUES (%s, %s, %s, %s, %s)",
            (url_id, user_id, url, summary, tags)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving stash: {e}")
        return False

def get_user_stashes(user_id):
    conn = get_db_connection()
    if not conn: return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM public.stashed_urls WHERE user_id = %s", (user_id,))
        stashes = cur.fetchall()
        cur.close()
        conn.close()
        return stashes
    except Exception as e:
        print(f"Error fetching stashes: {e}")
        return []

def delete_stash(stash_id):
    conn = get_db_connection()
    if not conn: return False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM public.stashed_urls WHERE url_id = %s", (stash_id,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting stash: {e}")
        return False