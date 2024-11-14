import requests
import pika
import json
import os
import logging
from flask import request, jsonify, make_response
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for Inventory API and RabbitMQ
INVENTORY_API_URL = os.getenv('INVENTORY_API_URL', "http://192.168.56.23:5014")
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', "localhost")
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'apiuser')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'password123')
QUEUE_NAME = "billing_queue"

def setup_routes(app):
    # Route for forwarding requests to the Inventory API
    @app.route('/api/inventory', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def handle_inventory():
        try:
            method = request.method
            url = urljoin(INVENTORY_API_URL, "inventory")
            data = request.get_json() if method in ['POST', 'PUT', 'DELETE'] else None

            logger.info(f"Forwarding {method} request to: {url}")
            logger.debug(f"Request data: {data}")

            # Set timeout for requests
            timeout = 5
            headers = {'Content-Type': 'application/json'}

            if method == 'GET':
                response = requests.get(url, timeout=timeout, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=timeout, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=timeout, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, timeout=timeout, headers=headers)

            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response content: {response.content}")

            try:
                return jsonify(response.json()), response.status_code
            except ValueError:
                return make_response(response.content, response.status_code)

        except requests.exceptions.Timeout:
            logger.error("Request to inventory service timed out")
            return jsonify({'error': 'Request timed out'}), 504
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to inventory service at {url}")
            return jsonify({'error': 'Service unavailable'}), 503
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return jsonify({'error': str(e)}), 500
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

    # Route for sending billing requests to RabbitMQ
    @app.route('/api/billing', methods=['POST'])
    def handle_billing():
        try:
            data = request.get_json()
            
            # Validate input
            required_fields = ('user_id', 'number_of_items', 'total_amount')
            if not data or not all(k in data for k in required_fields):
                logger.warning(f"Invalid billing request: missing required fields")
                return jsonify({'error': f'Invalid input. Required fields: {required_fields}'}), 400
            
            # Configure RabbitMQ connection with retry mechanism
            connection = None
            retry_count = 3
            retry_delay = 1

            # Set up credentials
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

            for attempt in range(retry_count):
                try:
                    connection = pika.BlockingConnection(
                        pika.ConnectionParameters(
                            host=RABBITMQ_HOST,
                            credentials=credentials,
                            connection_attempts=3,
                            retry_delay=1
                        )
                    )
                    channel = connection.channel()
                    channel.queue_declare(queue=QUEUE_NAME, durable=True)

                    message = json.dumps(data)
                    channel.basic_publish(
                        exchange='',
                        routing_key=QUEUE_NAME,
                        body=message,
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # Make message persistent
                            content_type='application/json'
                        )
                    )
                    
                    logger.info(f"Successfully queued billing request")
                    break
                except pika.exceptions.AMQPConnectionError as e:
                    logger.error(f"RabbitMQ connection attempt {attempt + 1} failed: {str(e)}")
                    if attempt == retry_count - 1:
                        raise
                    import time
                    time.sleep(retry_delay)
                finally:
                    if connection and not connection.is_closed:
                        connection.close()

            return jsonify({'status': 'Billing request received and queued'}), 200

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            return jsonify({'error': f"RabbitMQ Connection Error: {str(e)}"}), 503
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request: {str(e)}")
            return jsonify({'error': 'Invalid JSON format'}), 400
        except Exception as e:
            logger.error(f"Unexpected error in billing handler: {str(e)}")
            return jsonify({'error': f"An error occurred: {str(e)}"}), 500