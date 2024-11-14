#!/bin/bash
# Install necessary packages
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib npm

# Install pm2 globally
sudo npm install -g pm2

# Stop any existing processes
pm2 delete all || true
sudo pkill -f "python3.*server.py"

# Create a virtual environment
python3 -m venv /vagrant/srcs/inventory-app/venv

# Activate the virtual environment
source /vagrant/srcs/inventory-app/venv/bin/activate

# Install Flask and other dependencies
pip install -r /vagrant/srcs/inventory-app/requirements.txt

# Set up PostgreSQL database and table
sudo -u postgres psql -c "CREATE DATABASE movies_db;"
sudo -u postgres psql -d movies_db -c "CREATE TABLE movies (id SERIAL PRIMARY KEY, name VARCHAR(100), quantity INTEGER);"

# Start the Flask Inventory API
/vagrant/scripts/start_services.sh