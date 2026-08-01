#!/usr/bin/env bash

set -e

: "${BILLING_DB_NAME:?BILLING_DB_NAME is required}"
: "${BILLING_DB_USER:?BILLING_DB_USER is required}"
: "${BILLING_DB_PASSWORD:?BILLING_DB_PASSWORD is required}"
: "${RABBITMQ_USER:?RABBITMQ_USER is required}"
: "${RABBITMQ_PASSWORD:?RABBITMQ_PASSWORD is required}"

APP_DIR="/apps/billing-app"

echo "======================================== 1. Updating OS and installing dependencies"
apt-get update -y
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib curl rabbitmq-server


echo "======================================== 2. Installing Node.js and PM2"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install -y nodejs
npm install -g pm2


echo "======================================== 3. Configuring PostgreSQL"
sudo -u postgres psql -c "CREATE USER ${BILLING_DB_USER} WITH PASSWORD '${BILLING_DB_PASSWORD}';"
sudo -u postgres psql -c "CREATE DATABASE ${BILLING_DB_NAME} OWNER ${BILLING_DB_USER};"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${BILLING_DB_NAME} TO ${BILLING_DB_USER};"


echo "======================================== 4. Configuring RabbitMQ"
systemctl enable rabbitmq-server
systemctl start rabbitmq-server
rabbitmqctl add_user ${RABBITMQ_USER} ${RABBITMQ_PASSWORD} || true
rabbitmqctl set_permissions -p / ${RABBITMQ_USER} ".*" ".*" ".*"


echo "======================================== 5. Setting up the Python Application"
cd $APP_DIR
cp /vagrant/.env $APP_DIR/.env
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


echo "======================================== 6. Starting the Application with PM2"
pm2 start server.py --name billing-app --interpreter ./venv/bin/python
pm2 startup
pm2 save