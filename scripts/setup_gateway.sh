#!/bin/bash
# Install necessary packages
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv npm

# Install pm2 globally
sudo npm install -g pm2

# Stop any existing processes
pm2 delete all || true
sudo pkill -f "python3.*server.py"

# Create a virtual environment
python3 -m venv /vagrant/srcs/api-gateway/venv

# Activate the virtual environment
source /vagrant/srcs/api-gateway/venv/bin/activate

# Install Flask and other dependencies
pip install -r /vagrant/srcs/api-gateway/requirements.txt

# Start the Flask API Gateway
/vagrant/scripts/start_services.sh