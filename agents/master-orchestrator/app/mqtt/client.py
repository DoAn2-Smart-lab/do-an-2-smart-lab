"""
Wrapper paho-mqtt cho Master Orchestrator Agent.

Dung API dong bo cua paho-mqtt (loop_start chay background thread) - du cho skeleton nay de
publish/subscribe hoat dong duoc. Khi tich hop that voi FastAPI AsyncIO (Tuan 3-4), can bridge
callback on_message vao asyncio event loop (vd qua asyncio.Queue) neu can await ket qua trong
route handler thay vi chi fire-and-forget.
"""
import json
import logging
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt
from pydantic import BaseModel

from app.mqtt.topics import PUBLISH_TOPICS

logger = logging.getLogger(__name__)


class OrchestratorMqttClient:
    def __init__(self, host: str, port: int = 1883, client_id: str = "master-orchestrator"):
        self._host = host
        self._port = port
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._handlers: Dict[str, Callable[[dict], None]] = {}

    def connect(self) -> None:
        self._client.connect(self._host, self._port)
        self._client.loop_start()

    def disconnect(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def publish(self, topic: str, payload: BaseModel) -> None:
        if topic not in PUBLISH_TOPICS:
            raise ValueError(
                f"Master Orchestrator khong duoc phep publish vao topic '{topic}' - xem "
                "docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (vd: 'lab/safety/command' "
                "chi danh rieng cho Safety Agent)."
            )
        self._client.publish(topic, payload.model_dump_json())

    def subscribe(self, topic: str, handler: Callable[[dict], None]) -> None:
        self._handlers[topic] = handler
        self._client.subscribe(topic)

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        logger.info("Da ket noi MQTT broker %s:%s (reason_code=%s)", self._host, self._port, reason_code)
        for topic in self._handlers:
            client.subscribe(topic)

    def _on_message(self, client, userdata, msg):
        handler = self._handlers.get(msg.topic)
        if handler is None:
            return
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            logger.warning("Payload khong phai JSON hop le tren topic %s", msg.topic)
            return
        handler(payload)


_client: Optional[OrchestratorMqttClient] = None


def init_client(host: str, port: int = 1883) -> OrchestratorMqttClient:
    global _client
    _client = OrchestratorMqttClient(host=host, port=port)
    return _client


def get_client() -> OrchestratorMqttClient:
    if _client is None:
        raise RuntimeError("MQTT client chua duoc khoi tao - goi init_client() truoc (xem app/main.py)")
    return _client
