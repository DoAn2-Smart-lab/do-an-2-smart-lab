"""
Entrypoint Master Orchestrator Agent.

Chay (tu thu muc agents/master-orchestrator/, sau khi da pip install -r requirements.txt
o thu muc goc du an):
    uvicorn app.main:app --reload
"""
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.mqtt.client import get_client, init_client

load_dotenv()

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))

app = FastAPI(title="Master Orchestrator Agent")
app.include_router(chat_router)


@app.on_event("startup")
def startup() -> None:
    client = init_client(host=MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
    client.connect()


@app.on_event("shutdown")
def shutdown() -> None:
    get_client().disconnect()
