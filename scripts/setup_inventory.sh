#!/usr/bin/env bash

set -e

: "${INVENTORY_DB_NAME:?INVENTORY_DB_NAME is required}"
: "${INVENTORY_DB_USER:?INVENTORY_DB_USER is required}"
: "${INVENTORY_DB_PASSWORD:?INVENTORY_DB_PASSWORD is required}"

echo "Updating system packages..."
apt-get update -y

echo "Installing Python, pip, venv, and PostgreSQL..."
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib curl

echo "Installing modern Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install -y nodejs
sudo npm install -g pm2

echo "Configuring PostgreSQL..."
sudo -u postgres psql << EOF
CREATE DATABASE ${INVENTORY_DB_NAME};
CREATE USER ${INVENTORY_DB_USER} WITH PASSWORD '${INVENTORY_DB_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${INVENTORY_DB_NAME} TO ${INVENTORY_DB_USER};
EOF

echo "Setting up Python virtual environment directory..."
cd /vagrant/srcs/inventory
rm -rf .venv
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt

pm2 start server.py --name inventory-app --interpreter .venv/bin/python
pm2 startup
pm2 save