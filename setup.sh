#!/bin/bash

# this script sets up the .env file for the backend application, filling in a secret key if it doesn't already exist

if [ ! -f .env ]; then
  echo "Creating .env file from template..."

  cp .env.example .env

  SECRET_KEY=$(openssl rand -hex 32)
  sed -i -e "s/CHANGE_THIS_BEFORE_DEPLOYMENT/$SECRET_KEY/g" .env
  echo ".env file created successfully."
else
  echo ".env file already exists. Skipping creation."
fi