from flask import Flask
from dotenv import load_dotenv
import os
from routing import setup_routes

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set up the routes for the API Gateway
setup_routes(app)

if __name__ == '__main__':
    # Get the port from environment variables or default to 8000
    port = int(os.getenv('FLASK_APP_PORT', 8000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)