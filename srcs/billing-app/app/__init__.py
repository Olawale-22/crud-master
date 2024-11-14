from app.billing import app, setup_rabbitmq

# Optionally, you can initialize the RabbitMQ listener here if required.
def start_billing_service():
    # Run the Flask app for handling REST requests
    app.run(port=5008)

def start_rabbitmq_listener():
    # Set up the RabbitMQ consumer to listen for incoming messages
    setup_rabbitmq()
