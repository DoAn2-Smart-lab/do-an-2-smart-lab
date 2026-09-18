"""
Wrapper paho-mqtt cho Safety & Practical Tutoring Agent.

Dung API dong bo cua paho-mqtt (loop_start chay background thread), cung phong cach voi
agents/master-orchestrator/app/mqtt/client.py. Khac voi Orchestrator, Safety Agent KHONG can co
che wait_for_ack (Safety Agent la ben *tra loi* ACK, khong phai ben cho ACK) nen bo phan do duoc
luoc bo cho gon.
"""
import json
import logging
import uuid
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt
from pydantic import BaseModel

from app.mqtt.topics import PUBLISH_TOPICS, TOPIC_QOS, TOPIC_RETAIN

logger = logging.getLogger(__name__)


class SafetyAgentMqttClient:
    def __init__(self, host: str, port: int = 1883, client_id: Optional[str] = None):
        self._host = host
        self._port = port
        client_id = client_id or f"safety-agent-{uuid.uuid4().hex[:8]}"
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
                f"Safety Agent khong duoc phep publish vao topic '{topic}' - xem "
                "docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (vd: khong tu publish "
                "type='request' len 'lab/safety/command', viec do la cua Master Orchestrator)."
            )
        qos = TOPIC_QOS.get(topic, 1)
        retain = TOPIC_RETAIN.get(topic, False)
        self._client.publish(topic, payload.model_dump_json(), qos=qos, retain=retain)

    def subscribe(self, topic: str, handler: Optional[Callable[[dict], None]] = None) -> None:
        if handler is not None:
            self._handlers[topic] = handler
        qos = TOPIC_QOS.get(topic, 1)
        self._client.subscribe(topic, qos=qos)

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        logger.info("Da ket noi MQTT broker %s:%s (reason_code=%s)", self._host, self._port, reason_code)
        for topic in self._handlers:
            client.subscribe(topic, qos=TOPIC_QOS.get(topic, 1))

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except json.JSONDecodeError:
            logger.warning("Payload khong phai JSON hop le tren topic %s", msg.topic)
            return

        handler = self._handlers.get(msg.topic)
        if handler is not None:
            handler(payload)


_client: Optional[SafetyAgentMqttClient] = None


def init_client(host: str, port: int = 1883, client_id: Optional[str] = None) -> SafetyAgentMqttClient:
    global _client
    _client = SafetyAgentMqttClient(host=host, port=port, client_id=client_id)
    return _client


def get_client() -> SafetyAgentMqttClient:
    if _client is None:
        raise RuntimeError("MQTT client chua duoc khoi tao - goi init_client() truoc (xem app/main.py)")
    return _client
