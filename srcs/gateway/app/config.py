import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    GATEWAY_HOST = os.getenv("GATEWAY_HOST")
    GATEWAY_PORT = int(os.getenv("GATEWAY_PORT"))
    INVENTORY_API_URL = os.getenv("INVENTORY_API_URL")
    BILLING_RABBITMQ_HOST = os.getenv("BILLING_RABBITMQ_HOST")
    BILLING_RABBITMQ_PORT = int(os.getenv("BILLING_RABBITMQ_PORT"))
    BILLING_RABBITMQ_USER = os.getenv("BILLING_RABBITMQ_USER")
    BILLING_RABBITMQ_PASSWORD = os.getenv("BILLING_RABBITMQ_PASSWORD")
    BILLING_RABBITMQ_QUEUE =  os.getenv("BILLING_RABBITMQ_QUEUE")
