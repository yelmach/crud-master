# CRUD Master Py

CRUD Master Py is a three-VM movie-streaming learning project. The gateway is
the only public entry point: it forwards movie requests to Inventory over HTTP
and queues billing requests in RabbitMQ for asynchronous processing.

## Architecture and design

| VM | Private IP | Responsibilities |
| --- | --- | --- |
| `gateway-vm` | `192.168.56.10` | Flask API Gateway on port 8000; HTTP proxy to Inventory; RabbitMQ publisher for Billing |
| `inventory-vm` | `192.168.56.11` | Inventory Flask API on port 8080 and PostgreSQL database `movies_db` |
| `billing-vm` | `192.168.56.12` | RabbitMQ, Billing consumer on port 5001, and PostgreSQL database `billing_db` |

The gateway returns the Inventory service's response unchanged. Billing is
deliberately asynchronous: a successful `POST /api/billing` confirms that
RabbitMQ stored the message, not that the order was already inserted into the
database. Durable messages remain queued while `billing-app` is stopped.

## Stack

- Python 3 and Flask
- SQLAlchemy / Flask-SQLAlchemy
- PostgreSQL
- RabbitMQ with `pika`
- Vagrant and VirtualBox
- PM2

## Prerequisites

Install Vagrant and a supported VM provider such as VirtualBox. The Vagrant
provisioners install the remaining runtime packages inside the VMs.

## Configuration

The committed root [.env](.env) centralizes configuration and is loaded by the
services and Vagrant. For this educational project, its development credentials
are intentionally committed; do not commit credentials in a real project.

Important settings:

- Gateway: `GATEWAY_HOST`, `GATEWAY_PORT`, `INVENTORY_API_URL`
- Inventory: `INVENTORY_HOST`, `INVENTORY_PORT`, `INVENTORY_DB_HOST`, `INVENTORY_DB_PORT`, `INVENTORY_DB_NAME`, `INVENTORY_DB_USER`, `INVENTORY_DB_PASSWORD`
- Billing: `BILLING_HOST`, `BILLING_PORT`, `BILLING_DB_HOST`, `BILLING_DB_PORT`, `BILLING_DB_NAME`, `BILLING_DB_USER`, `BILLING_DB_PASSWORD`
- RabbitMQ: `BILLING_RABBITMQ_HOST`, `BILLING_RABBITMQ_PORT`, `BILLING_RABBITMQ_USER`, `BILLING_RABBITMQ_PASSWORD`, `BILLING_RABBITMQ_QUEUE`, `BILLING_RABBITMQ_HEARTBEAT`, `BILLING_RABBITMQ_BLOCKED_CONNECTION_TIMEOUT`, `BILLING_CONSUMER_RECONNECT_DELAY`

When using the VMs, `BILLING_RABBITMQ_HOST` must be `192.168.56.12`, not
`localhost`. The billing provisioner creates the configured RabbitMQ user on
each run. It must not be RabbitMQ's default `guest` account, because `guest`
accepts only local connections.

## Build and run

From the repository root:

```bash
vagrant up
vagrant status
```

The gateway and inventory ports are forwarded to the host, so the API is
available at `http://localhost:8000`. Billing port 5001 is also forwarded for
its health check. To rebuild a VM after a provisioning-script change:

```bash
vagrant provision billing-vm
vagrant provision gateway-vm
```

`vagrant reload` only reboots a VM; it does not rerun provisioning unless used
with `--provision`.

## Gateway API

The complete request and response contract is in [openapi.yaml](openapi.yaml).

- `GET /api/movies` and `GET /api/movies?title=<text>`
- `POST /api/movies`
- `DELETE /api/movies`
- `GET`, `PUT`, and `DELETE /api/movies/<id>`
- `POST /api/billing`

Create a movie through the gateway:

```bash
curl -X POST http://localhost:8000/api/movies \
  -H 'Content-Type: application/json' \
  -d '{"title":"Interstellar","description":"A science-fiction film."}'
```

Queue a billing order:

```bash
curl -X POST http://localhost:8000/api/billing \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"20","number_of_items":"2","total_amount":"250"}'
```

Expected billing response:

```json
{"message":"Message posted"}
```

## Verify the asynchronous billing flow

Confirm each application is running:

```bash
vagrant ssh gateway-vm -c 'sudo pm2 list'
vagrant ssh inventory-vm -c 'sudo pm2 list'
vagrant ssh billing-vm -c 'sudo pm2 list'
vagrant ssh billing-vm -c 'curl http://127.0.0.1:5001/health'
```

Stop the consumer, post a billing request, then start it again:

```bash
vagrant ssh billing-vm -c 'sudo pm2 stop billing-app'
# Run the billing curl request above; it should still return 200.
vagrant ssh billing-vm -c 'sudo pm2 start billing-app'
vagrant ssh billing-vm -c "sudo -u postgres psql -d billing_db -c 'SELECT * FROM orders;'"
```

The queued order appears after the consumer restarts. RabbitMQ is independent
of the Billing Flask process, which is why publishing still works while that
process is stopped.

## Testing and operations

Test every Gateway endpoint with Postman or an equivalent client, including
success, validation, not-found, and unavailable-service cases. Export the test
collection so it can be rerun during the project audit.

Useful commands:

```bash
vagrant ssh <vm-name>
sudo pm2 list
sudo pm2 restart <app-name>
sudo pm2 logs <app-name>
```

The PM2 application names are `gateway-app`, `inventory-app`, and `billing-app`.

## Repository layout

```text
.
├── .env
├── openapi.yaml
├── Vagrantfile
├── scripts/                 # VM provisioning scripts
├── srcs/gateway/            # Public API Gateway
├── srcs/inventory/          # Movie CRUD service
└── srcs/billing/            # RabbitMQ consumer and order storage
```
