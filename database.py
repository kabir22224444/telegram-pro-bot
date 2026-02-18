import psycopg2, os
from datetime import datetime

DB_URL = os.getenv("DB_URL")

def get_conn():
    return psycopg2.connect(DB_URL)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id SERIAL PRIMARY KEY,
            order_id TEXT,
            user_id BIGINT,
            service TEXT,
            game TEXT,
            status TEXT,
            created_at TIMESTAMP
        )
        """)
        conn.commit()

def save_order(order_id, user_id, service, game, status="PENDING"):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders(order_id,user_id,service,game,status,created_at) VALUES(%s,%s,%s,%s,%s,%s)",
            (order_id,user_id,service,game,status,datetime.now())
        )
        conn.commit()

def update_status(order_id, status):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE orders SET status=%s WHERE order_id=%s",
            (status, order_id)
        )
        conn.commit()
