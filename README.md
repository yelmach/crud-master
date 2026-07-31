# CRUD Master Py

CRUD Master Py is a small microservices API built around a movie catalog and a billing flow. The gateway accepts client requests, forwards movie CRUD operations to the Inventory service, and publishes billing orders to RabbitMQ so the Billing service can persist them in PostgreSQL.

## Stack

- Python 3
- Flask
- SQLAlchemy and Flask-SQLAlchemy
- PostgreSQL
- RabbitMQ
- Vagrant
- PM2

## Project Layout

```text
.
├── openapi.yaml
├── README.md
├── Vagrantfile
├── scripts/
│   ├── setup_billing.sh
│   ├── setup_gateway.sh
│   └── setup_inventory.sh
└── srcs/
        ├── billing/
        ├── gateway/
        └── inventory/
```

## Architecture

- Inventory service: stores movie data in PostgreSQL and exposes the movie CRUD API.
- Billing service: consumes RabbitMQ messages and stores billing orders in PostgreSQL.
- Gateway service: exposes the public API, proxies movie requests to Inventory, and queues billing requests in RabbitMQ.

The public HTTP contract is documented in [openapi.yaml](openapi.yaml).

## Requirements

- Python 3 and `pip`
- PostgreSQL
- RabbitMQ
- Vagrant and VirtualBox if you want to use the provided VM-based setup

The services load configuration from the repository root `.env` file. The most important variables are:

- `GATEWAY_HOST`
- `GATEWAY_PORT`
- `INVENTORY_HOST`
- `INVENTORY_PORT`
- `INVENTORY_API_URL`
- `INVENTORY_DB_HOST`
- `INVENTORY_DB_PORT`
- `INVENTORY_DB_NAME`
- `INVENTORY_DB_USER`
- `INVENTORY_DB_PASSWORD`
- `BILLING_HOST`
- `BILLING_PORT`
- `BILLING_DB_HOST`
- `BILLING_DB_PORT`
- `BILLING_DB_NAME`
- `BILLING_DB_USER`
- `BILLING_DB_PASSWORD`
- `BILLING_RABBITMQ_HOST`
- `BILLING_RABBITMQ_PORT`
- `BILLING_RABBITMQ_USER`
- `BILLING_RABBITMQ_PASSWORD`
- `BILLING_RABBITMQ_QUEUE`

## Run With Vagrant

The repository includes setup scripts for each service. From the project root, bring the VMs or services up with Vagrant, then SSH into the VM you want to inspect.

```bash
vagrant up
vagrant ssh billing-vm
```

Provisioning installs the runtime dependencies, creates the databases and users where needed, sets up a Python virtual environment, and starts the applications with PM2.

If you change a setup script, rerun provisioning rather than a plain reload:

```bash
vagrant provision billing-vm
```

## Run Locally

Each service can also be started directly from its own folder after the dependencies and `.env` file are in place.

Billing service:

```bash
cd srcs/billing
python3 -m pip install -r requirements.txt
python3 server.py
```

Gateway service:

```bash
cd srcs/gateway
python3 -m pip install -r requirements.txt
python3 server.py
```

Inventory service:

```bash
cd srcs/inventory
python3 -m pip install -r requirements.txt
python3 server.py
```

## Smoke Tests

This repository does not ship an automated test suite, so the safest validation is to run a few HTTP and messaging smoke tests after startup.

Check the Billing service health endpoint:

```bash
curl http://127.0.0.1:5001/health
```

Check the Gateway health or reachability through the public port configured in `.env`:

```bash
curl http://127.0.0.1:8000/
```

Test the billing publish path through the gateway:

```bash
curl -X POST http://127.0.0.1:8000/api/billing \
    -H 'Content-Type: application/json' \
    -d '{"user_id":"20","number_of_items":"99","total_amount":"250"}'
```

Expected response:

```json
{"message":"Message posted"}
```

If you want to validate end-to-end billing persistence, publish a message to RabbitMQ and then inspect the `orders` table in PostgreSQL from the Billing VM.

## API Overview

Gateway routes:

- `GET /api/movies`
- `POST /api/movies`
- `DELETE /api/movies`
- `GET /api/movies/<id>`
- `PUT /api/movies/<id>`
- `DELETE /api/movies/<id>`
- `POST /api/billing`

Billing service routes:

- `GET /`
- `GET /health`
- `GET /api/health`

## Notes

- `pm2` is used to keep the services running inside the VMs.
- `openapi.yaml` is the best source of truth for the public gateway contract.
- The setup scripts in `scripts/` are the canonical provisioning entrypoints for each service.

