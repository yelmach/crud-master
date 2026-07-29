# Billing Work Plan

Use this checklist to finish the billing and RabbitMQ part of the project in a clear order.

## Phase 1: Base setup

- [X] Confirm the environment variables needed for RabbitMQ and PostgreSQL.
- [X] Define the `billing_db` connection settings in `srcs/billing/app/config.py`.
- [X] Verify the billing service starts cleanly with `python server.py`.

## Phase 2: Database layer

- [x] Create or validate the `orders` table schema.
- [x] Add the model or persistence logic for inserting new billing orders.
- [x] Make sure database connection errors are handled clearly.

## Phase 3: RabbitMQ consumer

- [x] Connect the billing service to the `billing_queue` queue.
- [x] Parse the incoming JSON message body.
- [x] Validate the required fields before inserting a row.
- [x] Save the order in PostgreSQL after a message is received.
- [x] Acknowledge the RabbitMQ message only after the insert succeeds.

## Phase 4: Queue resilience

- [ ] Configure the queue so messages are durable.
- [ ] Make the consumer recover after a stop and restart.
- [ ] Check that pending messages are processed after the billing service comes back online.

## Phase 5: Gateway integration

- [ ] Implement `POST /api/billing` in the gateway.
- [ ] Publish the request body to RabbitMQ without blocking the client.
- [ ] Return a success response as soon as the message is queued.
- [ ] Make sure the gateway still accepts requests even if the billing service is stopped.

## Phase 6: Testing

- [ ] Test a valid billing message from the gateway.
- [ ] Test direct publishing to `billing_queue`.
- [ ] Test that invalid JSON or missing fields are rejected safely.
- [ ] Test the stop and restart scenario to confirm queued messages are processed later.

## Phase 7: Documentation

- [ ] Document the RabbitMQ queue name, database name, and required ports.
- [ ] Note the manual test steps used during development.
- [ ] Keep any billing-specific instructions separate from the main README if needed.

## Suggested order

1. Database setup
2. RabbitMQ consumer
3. Queue resilience
4. Gateway publishing route
5. End-to-end testing
6. Documentation
