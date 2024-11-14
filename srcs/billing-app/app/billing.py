import psycopg2
import pika
import json
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Function to get the database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_BILLING'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    return conn

# Function to process messages from RabbitMQ
def process_billing_message(ch, method, properties, body):
    message = json.loads(body)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO orders (user_id, number_of_items, total_amount) VALUES (%s, %s, %s)',
        (message['user_id'], message['number_of_items'], message['total_amount'])
    )
    conn.commit()
    cur.close()
    conn.close()
    ch.basic_ack(delivery_tag=method.delivery_tag)

def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBITMQ_HOST', 'localhost')))
    channel = connection.channel()
    channel.queue_declare(queue='billing_queue', durable=True)
    channel.basic_consume(queue='billing_queue', on_message_callback=process_billing_message)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

@app.route('/billing', methods=['POST'])
def add_billing():
    return jsonify({'error': 'Use the API Gateway to submit billing requests.'}), 400

if __name__ == '__main__':
    # Start the RabbitMQ consumer in a separate thread or process
    import threading
    rabbitmq_thread = threading.Thread(target=setup_rabbitmq, daemon=True)
    rabbitmq_thread.start()
    
    port = int(os.getenv("FLASK_APP_PORT", 5008))
    app.run(host='0.0.0.0', port=port, use_reloader=False)