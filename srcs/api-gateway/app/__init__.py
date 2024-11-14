from flask import Flask
from .routing import setup_routes

app = Flask(__name__)

# Set up the routes for the API Gateway
setup_routes(app)