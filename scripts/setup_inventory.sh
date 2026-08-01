#!/usr/bin/env bash

set -e

: "${INVENTORY_DB_NAME:?INVENTORY_DB_NAME is required}"
: "${INVENTORY_DB_USER:?INVENTORY_DB_USER is required}"
: "${INVENTORY_DB_PASSWORD:?INVENTORY_DB_PASSWORD is required}"

APP_DIR="/apps/inventory-app"

echo "======================================== 1. Updating OS and installing dependencies"
apt-get update -y
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib curl


echo "======================================== 2. Installing Node.js and PM2"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install -y nodejs
npm install -g pm2


echo "======================================== 3. Configuring PostgreSQL"
sudo -u postgres psql -c "CREATE USER ${INVENTORY_DB_USER} WITH PASSWORD '${INVENTORY_DB_PASSWORD}';"
sudo -u postgres psql -c "CREATE DATABASE ${INVENTORY_DB_NAME} OWNER ${INVENTORY_DB_USER};"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${INVENTORY_DB_NAME} TO ${INVENTORY_DB_USER};"


echo "======================================== 4. Setting up the Python Application"
cd $APP_DIR
cp /vagrant/.env $APP_DIR/.env
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


echo "======================================== 5. Starting the Application with PM2"
pm2 start server.py --name inventory-app --interpreter ./venv/bin/python
pm2 startup
pm2 save