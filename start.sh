#!/bin/bash

# Init the database with test data
echo "Init database..."
source ./venv/bin/activate && python -m backend.app --dropall --initonly

# Stop any existing uwsgi server
echo "Stopping old uwsgi..."
./stop.sh

# Start the WSGI server so the Flask app can receive requests from NGIN
echo "Starting uwsgi..."
source ./venv/bin/activate && uwsgi --ini wsgi.ini &

# Reload nginx
echo "Starting nginx..."
sudo nginx -s reload

