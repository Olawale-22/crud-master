import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_INVENTORY', 'movies_db'),
            user=os.getenv('DB_USER', 'apiuser'),
            password=os.getenv('DB_PASSWORD', 'crud-master')
        )
        logger.debug("Database connection established")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

def add_item(data):
    try:
        logger.debug(f"Adding item with data: {data}")
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Validate required fields
        required_fields = ['name', 'quantity']
        if not all(field in data for field in required_fields):
            raise ValueError(f"Missing required fields. Required: {required_fields}")
            
        cur.execute(
            'INSERT INTO movies (name, quantity) VALUES (%s, %s) RETURNING id;',
            (data['name'], data['quantity'])
        )
        item_id = cur.fetchone()[0]
        conn.commit()
        
        # Fetch the created item
        cur.execute('SELECT * FROM movies WHERE id = %s;', (item_id,))
        item = cur.fetchone()
        
        cur.close()
        conn.close()
        
        logger.info(f"Successfully added item with id: {item_id}")
        return {'id': item[0], 'name': item[1], 'quantity': item[2]}
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error adding item: {str(e)}")
        raise

def get_all_items():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM movies;')
        items = cur.fetchall()
        cur.close()
        conn.close()
        return items
    except Exception as e:
        logger.error(f"Error getting items: {str(e)}")
        raise