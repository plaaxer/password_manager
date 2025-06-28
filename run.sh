#!/bin/bash

# This script automates the startup process for the Password Manager.

echo "--- Password Manager Startup ---"

# Step 1: Start the backend services (API + Database) in the background.
echo "Starting backend services... (This may take a moment)"
docker-compose up -d --build

# Step 2: Add a small delay to give the services time to initialize.
# The database and API might need a few seconds to be fully ready.
echo "Waiting for services to initialize..."
sleep 3

# Step 3: Launch the Python GUI application.
# This script will now wait here until you close the GUI window.
echo "Launching GUI..."
python3 frontend/gui.py

# Step 4: (Optional but Recommended) Clean up after the GUI is closed.
# The 'docker-compose down' command stops and removes the containers.
echo "GUI closed. Shutting down backend services..."
docker-compose down

echo "--- Shutdown complete. ---"