#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

APP_DIR="/vagrant/srcs/billing"
APP_NAME="billing-app"
VENV_DIR="${APP_DIR}/venv"
PM2_SERVICE_FILE="/etc/systemd/system/billing-pm2.service"

: "${BILLING_RABBITMQ_USER:?BILLING_RABBITMQ_USER is required}"
: "${BILLING_RABBITMQ_PASSWORD:?BILLING_RABBITMQ_PASSWORD is required}"

sudo apt-get update
sudo apt-get install -y curl gnupg2 ca-certificates lsb-release apt-transport-https software-properties-common python3 python3-venv python3-pip postgresql postgresql-contrib rabbitmq-server

if ! command -v node >/dev/null 2>&1; then
	curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
	sudo apt-get install -y nodejs
fi

sudo npm install -g pm2
PM2_BIN="$(command -v pm2)"

sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server

sudo rabbitmqctl add_user "${BILLING_RABBITMQ_USER}" "${BILLING_RABBITMQ_PASSWORD}"
sudo rabbitmqctl set_permissions -p / "${BILLING_RABBITMQ_USER}" '.*' '.*' '.*'

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = 'billing_db'" | grep -q 1 || sudo -u postgres createdb billing_db
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname = 'billing_user'" | grep -q 1 || sudo -u postgres psql -c "CREATE USER billing_user WITH PASSWORD 'billing_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE billing_db TO billing_user;"
sudo -u postgres psql -d billing_db -c "GRANT ALL ON SCHEMA public TO billing_user;"

cd "${APP_DIR}"
python3 -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r requirements.txt

if "${PM2_BIN}" describe "${APP_NAME}" >/dev/null 2>&1; then
	"${PM2_BIN}" delete "${APP_NAME}" || true
fi

"${PM2_BIN}" start "${VENV_DIR}/bin/python3" --name "${APP_NAME}" --cwd "${APP_DIR}" -- server.py
"${PM2_BIN}" save

cat > "${PM2_SERVICE_FILE}" <<EOF
[Unit]
Description=PM2 service for billing app
After=network-online.target postgresql.service rabbitmq-server.service
Wants=network-online.target

[Service]
Type=forking
User=root
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
Environment=PM2_HOME=/root/.pm2
PIDFile=/root/.pm2/pm2.pid
ExecStart=${PM2_BIN} resurrect
ExecReload=${PM2_BIN} reload all
ExecStop=${PM2_BIN} kill
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable billing-pm2.service
systemctl restart billing-pm2.service
