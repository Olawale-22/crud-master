#!/bin/bash

cleanup_processes() {
    # Stop any existing Python processes using the port
    PORT=$1
    PID=$(sudo lsof -t -i:$PORT)
    if [ ! -z "$PID" ]; then
        echo "Stopping existing process on port $PORT"
        sudo kill -9 $PID
    fi
    
    # Clean up pm2 processes
    pm2 delete all || true
}

# Start services for the API Gateway
if [ "$(hostname)" == "api-gateway" ]; then
    echo "Starting API Gateway services..."
    cleanup_processes 8000
    source /vagrant/srcs/api-gateway/venv/bin/activate
    pm2 start /vagrant/srcs/api-gateway/app/server.py --interpreter python3 --name api-gateway --no-autorestart
fi

# Start services for the Inventory API
if [ "$(hostname)" == "inventory-app" ]; then
    echo "Starting Inventory API services..."
    cleanup_processes 5014
    source /vagrant/srcs/inventory-app/venv/bin/activate
    pm2 start /vagrant/srcs/inventory-app/server.py --interpreter python3 --name inventory-api --no-autorestart
fi

# Start services for the Billing API
if [ "$(hostname)" == "billing-app" ]; then
    echo "Starting Billing API services..."
    cleanup_processes 5008
    source /vagrant/srcs/billing-app/venv/bin/activate
    pm2 start /vagrant/srcs/billing-app/server.py --interpreter python3 --name billing-api --no-autorestart
fi