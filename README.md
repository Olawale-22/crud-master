# CRUD-MASTER (A Microservices Project)

This project consists of multiple microservices for managing inventory and billing. The services are deployed using Vagrant and configured to use PostgreSQL and RabbitMQ.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Configuration](#database-configuration)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)

## Project Overview

This project demonstrates a microservices architecture with the following components:

- **API Gateway**: Routes requests to the appropriate microservice.
- **Inventory Service**: Manages inventory items.
- **Billing Service**: Handles billing requests and queues them using RabbitMQ.

## Architecture

- **API Gateway**: Acts as a single entry point for all client requests.
- **Inventory Service**: Provides CRUD operations for inventory items.
- **Billing Service**: Queues billing requests using RabbitMQ.
![CRUD Master Diagram](./crud-master-diagram.png)


## Prerequisites

- [Vagrant](https://www.vagrantup.com/downloads)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Setup and Installation

After cloning the repository, navigate to the project directory:

```bash
cd crud-master
```

Launch the Vagrant environment:
```bash
vagrant up
```
Configuration
Ensure your `.env` files are correctly configured for each service:

API Gateway `.env`
Create the following .env file in the `crud-master/srcs/api-gateway/` path:

```bash
INVENTORY_API_URL=http://192.168.56.23:5014
RABBITMQ_HOST=192.168.56.24
FLASK_APP_PORT=8000
```

Inventory API `.env`
Create the following `.env` file in the `crud-master/srcs/inventory-app/` path:
```bash 
DB_HOST=localhost
DB_PORT=5432
DB_USER=apiuser
DB_PASSWORD=crud-master
DB_INVENTORY=movies_db
FLASK_APP_PORT=5014
```
Billing API .env
Create the following `.env` file in the `crud-master/srcs/billing-app/` path:

```bash 
DB_HOST=localhost
DB_PORT=5432
DB_USER=apiuser
DB_PASSWORD=crud-master
DB_BILLING=billing_db
RABBITMQ_HOST=localhost
RABBITMQ_USER=apiuser
RABBITMQ_PASS=password123
QUEUE_NAME=billing_queue
FLASK_APP_PORT=5008
```

Database Configuration
Edit the PostgreSQL configuration file if you are running it locally:
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```
Ensure the following lines are present:

```bash
local   all             postgres                                peer
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```
What we did here was change places where you would probably see `peer` in the config file to `md5`, except for the postgres line.

Restart PostgreSQL afterwards:
```bash
sudo systemctl restart postgresql
```
Logs & Services
API Gateway
```bash
vagrant ssh gateway-vm
pm2 list
pm2 logs api-gateway
```

Inventory API
```bash
vagrant ssh inventory-vm
pm2 list
pm2 logs inventory-api
```
Billing API
```bash
vagrant ssh billing-vm
pm2 list
pm2 logs billing-api
```

Usage
Testing the Inventory API (PowerShell)
You may use curl if you like:
```bash
$headers = @{
    "Content-Type" = "application/json"
    "Accept" = "application/json"
}

$body = @{
    name = "movie"
    quantity = 10
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://192.168.56.22:8000/api/inventory" -Method Post -Headers $headers -Body $body -Verbose

$response | ConvertTo-Json
```
Testing the Billing API (PowerShell)
```bash
$headers = @{
    "Content-Type" = "application/json"
    "Accept" = "application/json"
}

$body = @{
    "user_id" = "3"
    "number_of_items" = "5"
    "total_amount" = "180"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://192.168.56.22:8000/api/billing" -Method Post -Headers $headers -Body $body -Verbose

$response | ConvertTo-Json
```
Have a great one...