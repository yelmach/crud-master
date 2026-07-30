# CRUD Master Py

CRUD Master Py is a small microservices project with three parts:

- an Inventory API for movie CRUD operations
- a Billing API that consumes RabbitMQ messages and stores orders in PostgreSQL
- an API Gateway that proxies movie requests over HTTP and queues billing requests through RabbitMQ

## Stack

- Python 3
- Flask
- SQLAlchemy and Flask-SQLAlchemy
- PostgreSQL
- RabbitMQ
- Vagrant
- PM2

## Repository layout

```text
.
├── openapi.yaml
├── README.md
├── Vagrantfile
├── .env
├── scripts/
│   ├── setup_billing.sh
│   ├── setup_gateway.sh
│   └── setup_inventory.sh
└── srcs/
    ├── billing/
    ├── gateway/
    └── inventory/
```

## Gateway API

The gateway exposes:

- `GET /api/movies`
- `POST /api/movies`
- `DELETE /api/movies`
- `GET /api/movies/<id>`
- `PUT /api/movies/<id>`
- `DELETE /api/movies/<id>`
- `POST /api/billing`

The full contract is documented in [openapi.yaml](openapi.yaml).

## Environment variables

The project uses the root [.env](.env) file. The important values are:

- `GATEWAY_HOST`
- `GATEWAY_PORT`
- `INVENTORY_API_URL`
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

## Run the billing service locally

From the billing folder:

```bash
cd srcs/billing
python3 -m pip install -r requirements.txt
python3 server.py
```

The billing service runs on the host and port defined in [.env](.env).

## Run the billing VM

From the project root:

```bash
vagrant up billing-vm
vagrant ssh billing-vm
```

The billing VM installs PostgreSQL, RabbitMQ, Python dependencies, and PM2.

## Test the billing API

Inside `billing-vm`:

```bash
sudo pm2 list
curl http://127.0.0.1:5001/health
```

To publish a billing message directly to RabbitMQ:

```bash
python3 - <<'PY'
import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()
channel.queue_declare(queue='billing_queue', durable=True)
channel.basic_publish(
    exchange='',
    routing_key='billing_queue',
    body=json.dumps({
        'user_id': '20',
        'number_of_items': '99',
        'total_amount': '250'
    }),
    properties=pika.BasicProperties(delivery_mode=2),
)
connection.close()
PY
```

Then check PostgreSQL:

```bash
sudo -u postgres psql -d billing_db -c "SELECT * FROM orders;"
```

## Test the gateway billing route

When `POST /api/billing` is implemented and the gateway is running:

```bash
curl -X POST http://127.0.0.1:8000/api/billing \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"20","number_of_items":"99","total_amount":"250"}'
```

Expected response:

```json
{"message":"Message posted"}
```

## Vagrant and PM2 notes

- `vagrant reload` reboots the VM, but it does not rerun provisioning.
- Use `vagrant provision billing-vm` or `vagrant reload --provision billing-vm` after changing the setup script.
- Inside the VM, PM2 commands are:

```bash
sudo pm2 list
sudo pm2 stop billing-app
sudo pm2 start billing-app
```

## Documentation files

- Gateway OpenAPI spec: [openapi.yaml](openapi.yaml)

