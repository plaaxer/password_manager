#!/bin/bash

# this script sets up the .env file for the backend application
# and then starts the application using Docker Compose.

if [ ! -f .env ]; then
  echo "Creating .env file from template..."

  if [ ! -f .env.example ]; then
    echo "Error: .env.example file not found. Cannot create .env file."
    exit 1
  fi

  cp .env.example .env

  # generate a new secret key and replace the placeholder
  SECRET_KEY=$(openssl rand -hex 32)

  # the command below works on both Linux (sed) and macOS (sed -i '')
  sed -i.bak "s/CHANGE_THIS_BEFORE_DEPLOYMENT/$SECRET_KEY/g" .env && rm .env.bak
  
  echo ".env file created successfully."
else
  echo ".env file already exists. Skipping creation."
fi

echo ""
echo "Starting the application with Docker Compose..."
echo "This may take a moment on the first run..."

docker compose up --build