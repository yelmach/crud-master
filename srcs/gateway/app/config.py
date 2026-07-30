import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

class Config:
    GATEWAY_HOST = os.getenv("GATEWAY_HOST")
    GATEWAY_PORT = int(os.getenv("GATEWAY_PORT"))
    INVENTORY_API_URL = os.getenv("INVENTORY_API_URL")
