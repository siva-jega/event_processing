#!/bin/bash

# Initialize the database
superset db upgrade

# Create default admin user
superset fab create-admin \
    --username admin \
    --firstname Superset \
    --lastname Admin \
    --email admin@superset.com \
    --password admin123

# Initialize Superset
superset init

# Start Superset
/usr/bin/run-server.sh