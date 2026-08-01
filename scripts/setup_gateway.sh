#!/usr/bin/env bash

set -e

APP_DIR="/apps/api-gateway-app"

echo "======================================== 1. Updating OS and installing dependencies"
apt-get update -y
apt-get install -y python3 python3-pip python3-venv curl


echo "======================================== 2. Installing Node.js and PM2"
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install -y nodejs
npm install -g pm2


echo "======================================== 3. Setting up the Python Application"
cd $APP_DIR
cp /vagrant/.env $APP_DIR/.env
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


echo "======================================== 4. Starting the Application with PM2"
pm2 start server.py --name gateway-app --interpreter ./venv/bin/python
pm2 startup
pm2 save