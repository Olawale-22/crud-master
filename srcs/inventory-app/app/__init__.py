import psycopg2
import os

# inventory.py
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_INVENTORY'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn


def get_all_items():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM movies;')
    items = cur.fetchall()
    cur.close()
    conn.close()
    return [{'id': item[0], 'name': item[1], 'quantity': item[2]} for item in items]

def get_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM movies WHERE id = %s;', (item_id,))
    item = cur.fetchone()
    cur.close()
    conn.close()
    return {'id': item[0], 'name': item[1], 'quantity': item[2]} if item else None

def add_item(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO movies (name, quantity) VALUES (%s, %s) RETURNING id;', 
                (data['name'], data['quantity']))
    item_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {'id': item_id, 'name': data['name'], 'quantity': data['quantity']}

def update_item(item_id, data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE movies SET name = %s, quantity = %s WHERE id = %s;', 
                (data['name'], data['quantity'], item_id))
    conn.commit()
    cur.close()
    conn.close()
    return get_item(item_id)

def delete_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM movies WHERE id = %s;', (item_id,))
    deleted_rows = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return deleted_rows > 0
