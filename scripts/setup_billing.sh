#!/bin/bash
# Install necessary packages
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv rabbitmq-server postgresql postgresql-contrib npm

# Install pm2 globally
sudo npm install -g pm2

# Stop any existing processes
pm2 delete all || true
sudo pkill -f "python3.*server.py"

# Create a virtual environment
python3 -m venv /vagrant/srcs/billing-app/venv

# Activate the virtual environment
source /vagrant/srcs/billing-app/venv/bin/activate

# Install Flask and other dependencies
pip install -r /vagrant/srcs/billing-app/requirements.txt

# Set up PostgreSQL database and table
sudo -u postgres psql -c "CREATE DATABASE billing_db;"
sudo -u postgres psql -d billing_db -c "CREATE TABLE orders (id SERIAL PRIMARY KEY, user_id INTEGER, number_of_items INTEGER, total_amount DECIMAL);"

# Start RabbitMQ server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

# Start the Flask Billing API
/vagrant/scripts/start_services.sh