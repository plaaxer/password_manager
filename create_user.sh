#!/bin/bash

username=$(whoami)

echo "Enter the password for the new PostgreSQL user:"
read -s password

echo "Confirm the password for the new PostgreSQL user:"
read -s password_confirm

if [ "$password" != "$password_confirm" ]; then
  echo "Passwords do not match. Exiting."
  exit 1
fi

echo "The user created for the database will be: $username"

sudo -i -u postgres bash <<EOF
psql -c "CREATE USER $username WITH PASSWORD '$password';"
psql -c "ALTER USER $username CREATEDB;"
EOF
