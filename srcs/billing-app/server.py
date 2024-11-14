from flask import Flask, request, jsonify
import pika
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
QUEUE_NAME = 'billing_queue'

@app.route('/billing', methods=['POST'])
def create_billing():
    data = request.get_json()
    if not data or not all(k in data for k in ('user_id', 'number_of_items', 'total_amount')):
        return jsonify({'error': 'Invalid input'}), 400

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        message = json.dumps(data)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        connection.close()
        return jsonify({'status': 'Billing request received and queued'}), 200
    except pika.exceptions.AMQPConnectionError as e:
        return jsonify({'error': f"RabbitMQ Connection Error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

# if __name__ == '__main__':
#     app.run(port=5008)

if __name__ == '__main__':
    port = int(os.getenv("FLASK_APP_PORT", 5008))
    app.run(host='0.0.0.0', port=port)