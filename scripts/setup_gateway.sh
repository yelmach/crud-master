#!/usr/bin/env bash

set -e

: "${GATEWAY_HOST:?GATEWAY_HOST is required}"
: "${GATEWAY_PORT:?GATEWAY_PORT is required}"
: "${INVENTORY_API_URL:?INVENTORY_API_URL is required}"

echo "Updating system packages..."
apt-get update -y

echo "Installing Python, pip, venv, and curl..."
apt-get install -y python3 python3-pip python3-venv curl

echo "Installing modern Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
apt-get install -y nodejs
sudo npm install -g pm2

echo "Setting up the Gateway virtual environment..."
cd /vagrant/srcs/gateway
rm -rf .venv
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt

pm2 start server.py --name gateway-app --interpreter .venv/bin/python
pm2 startup
pm2 save
