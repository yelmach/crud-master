# crud-master

## Recommended division

### Yelmach

#### 1. Inventory service

Implement:

* PostgreSQL `movies_db`
* Movie model and table
* All movie CRUD endpoints
* Search/filter by title
* Validation and HTTP error handling

#### 2. Gateway inventory routing

Implement Gateway routes for:

```text
/api/movies
/api/movies/<id>
```

The Gateway should forward:

* HTTP method
* JSON body
* Query parameters
* Status code
* Response body

#### 3. Vagrant infrastructure

After agreeing on ports, service names and environment variables, create:

* `gateway-vm`
* `inventory-vm`
* `billing-vm`
* Private network IPs
* Provisioning scripts
* Environment-variable injection
* PM2 startup configuration

You can start the `Vagrantfile` early, but finish provisioning after both applications are stable.

---

### Azzouzi

#### 1. Billing service

Implement:

* PostgreSQL `billing_db`
* Orders table
* RabbitMQ consumer
* JSON validation
* Database insertion
* Manual message acknowledgement

#### 2. RabbitMQ

Configure:

* Durable `billing_queue`
* Persistent messages
* User and password
* Access from the Gateway VM
* Reconnection after service restart

#### 3. Gateway billing routing

Implement:

```text
POST /api/billing
```

This route should publish the order to RabbitMQ and return immediately.

This is a logical assignment because your teammate owns both sides of the billing flow:

```text
Gateway producer → RabbitMQ → Billing consumer
```

#### 4. Testing and documentation

Prepare:

* Postman collection
* OpenAPI specification
* README
* Endpoint tests
* RabbitMQ resilience test
* Clean installation instructions

## Best parallel workflow

### Phase 1 — Work independently

**Yelmach**

```text
Inventory API
Gateway movie proxy
Basic Vagrantfile
```

**Azzouzi**

```text
Billing consumer
RabbitMQ setup
Gateway billing producer
```

### Phase 2 — Integration

Merge both Gateway parts carefully:

```text
Gateway
├── Movie routes
└── Billing route
```

Avoid both editing the same main Gateway file. Separate routes into modules:

```text
gateway/
├── app.py
├── routes/
│   ├── inventory_routes.py
│   └── billing_routes.py
└── services/
    ├── inventory_client.py
    └── rabbitmq_publisher.py
```

This reduces Git conflicts.

### Phase 3 — Infrastructure and testing

**Yelmach** finish VM provisioning while **Azzouzi** prepares tests and documentation.

Test the entire project from a clean environment.

## One important thing

Each person should test their own implementation first
