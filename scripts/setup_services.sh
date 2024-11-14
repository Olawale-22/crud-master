#!/bin/bash

# Function to set up RabbitMQ
setup_rabbitmq() {
  echo "Setting up RabbitMQ..."

  # Add RabbitMQ user
  sudo rabbitmqctl add_user apiuser password123

  # Set user tags
  sudo rabbitmqctl set_user_tags apiuser administrator

  # Set permissions for the user on the virtual host '/'
  sudo rabbitmqctl set_permissions -p / apiuser ".*" ".*" ".*"

  # Restart RabbitMQ
  sudo systemctl restart rabbitmq-server

  echo "RabbitMQ setup completed."
}

# Function to set up PostgreSQL for billing
setup_postgresql_billing() {
  echo "Setting up PostgreSQL for billing..."

  # Create PostgreSQL user and database
  sudo -u postgres psql <<EOF
CREATE USER apiuser WITH PASSWORD 'crud-master';
ALTER USER apiuser WITH SUPERUSER;
CREATE DATABASE billing_db;
GRANT ALL PRIVILEGES ON DATABASE billing_db TO apiuser;
EOF

  # Change ownership of the database
  sudo -u postgres psql <<EOF
ALTER DATABASE billing_db OWNER TO apiuser;
\c billing_db
REASSIGN OWNED BY postgres TO apiuser;
DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = current_schema() LOOP
        EXECUTE 'ALTER TABLE ' || quote_ident(r.tablename) || ' OWNER TO apiuser';
    END LOOP;
END \$\$;
DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = current_schema() LOOP
        EXECUTE 'ALTER SEQUENCE ' || quote_ident(r.sequence_name) || ' OWNER TO apiuser';
    END LOOP;
END \$\$;
DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT table_name FROM information_schema.views WHERE table_schema = current_schema() LOOP
        EXECUTE 'ALTER VIEW ' || quote_ident(r.table_name) || ' OWNER TO apiuser';
    END LOOP;
END \$\$;
EOF

  # Restart PostgreSQL
  sudo systemctl restart postgresql

  echo "PostgreSQL setup for billing completed."
}

# Function to set up PostgreSQL for inventory
setup_postgresql_inventory() {
  echo "Setting up PostgreSQL for inventory..."

  # Create PostgreSQL user and database
  sudo -u postgres psql <<EOF
CREATE USER apiuser WITH PASSWORD 'crud-master';
ALTER USER apiuser WITH SUPERUSER;
CREATE DATABASE movies_db;
GRANT ALL PRIVILEGES ON DATABASE movies_db TO apiuser;
EOF

  # Change ownership of the database
  sudo -u postgres psql <<EOF
ALTER DATABASE movies_db OWNER TO apiuser;
\c movies_db
REASSIGN OWNED BY postgres TO apiuser;
DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = current_schema() LOOP
        EXECUTE 'ALTER TABLE ' || quote_ident(r.tablename) || ' OWNER TO apiuser';
    END LOOP;
END \$\$;
DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = current_schema() LOOP
        EXECUTE 'ALTER SEQUENCE ' || quote_ident(r.sequence_name) || ' OWNER TO apiuser';
    END LOOP;
END \$\$;
DO \$\$ DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT table_name FROM information_schema.views WHERE table_schema = current_schema() LOOP
        EXECUTE 'ALTER VIEW ' || quote_ident(r.table_name) || ' OWNER TO apiuser';
    END LOOP;
END \$\$;
EOF

  # Restart PostgreSQL
  sudo systemctl restart postgresql

  echo "PostgreSQL setup for inventory completed."
}

# Run the setup functions based on the hostname
if [ "$(hostname)" == "billing-app" ]; then
  setup_rabbitmq
  setup_postgresql_billing
elif [ "$(hostname)" == "inventory-app" ]; then
  setup_postgresql_inventory
fi