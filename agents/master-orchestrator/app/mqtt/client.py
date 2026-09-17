"""
Wrapper paho-mqtt cho Master Orchestrator Agent.

Dung API dong bo cua paho-mqtt (loop_start chay background thread). Ngoai publish/subscribe co
ban, co them wait_for_ack() de thay the wait_response dang la placeholder: publish 1 request len
lab/safety/command, roi cho message co "in_reply_to" khop message_id cua request do, toi da
`timeout` giay (mac dinh 3s theo docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md).

Co che khop "in_reply_to" nay KHONG rieng cho topic nao - bat ky message nao co field
"in_reply_to" tren bat ky topic da subscribe deu duoc doi chieu, nen ve sau co the tai su dung
cho lab/data/result neu can (hien tai chi lab/safety/command dung thuc te).
"""
import json
import logging
import threading
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt
from pydantic import BaseModel

from app.mqtt.topics import PUBLISH_TOPICS, TOPIC_QOS, TOPIC_RETAIN

logger = logging.getLogger(__name__)


class OrchestratorMqttClient:
    def __init__(self, host: str, port: int = 1883, client_id: str = "master-orchestrator"):
        self._host = host
        self._port = port
        self._client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._handlers: Dict[str, Callable[[dict], None]] = {}

        # Co che cho ACK: message_id dang cho -> threading.Event, va ket qua tra ve tuong ung.
        self._pending_acks: Dict[str, threading.Event] = {}
        self._ack_results: Dict[str, dict] = {}
        self._ack_lock = threading.Lock()

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
                "docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (vd: khong tu publish "
                "type='ack' hoac lenh dong/cat contactor len 'lab/safety/command')."
            )
        qos = TOPIC_QOS.get(topic, 1)
        retain = TOPIC_RETAIN.get(topic, False)
        self._client.publish(topic, payload.model_dump_json(), qos=qos, retain=retain)

    def subscribe(self, topic: str, handler: Optional[Callable[[dict], None]] = None) -> None:
        if handler is not None:
            self._handlers[topic] = handler
        qos = TOPIC_QOS.get(topic, 1)
        self._client.subscribe(topic, qos=qos)

    def wait_for_ack(self, message_id: str, timeout: float = 3.0) -> Optional[dict]:
        """Cho message co 'in_reply_to' == message_id, toi da `timeout` giay.
        Tra ve payload (dict) neu nhan duoc kip, hoac None neu het gio (timeout)."""
        event = threading.Event()
        with self._ack_lock:
            self._pending_acks[message_id] = event

        got_reply = event.wait(timeout)

        with self._ack_lock:
            self._pending_acks.pop(message_id, None)
            result = self._ack_results.pop(message_id, None)

        return result if got_reply else None

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

        in_reply_to = payload.get("in_reply_to")
        if in_reply_to:
            with self._ack_lock:
                event = self._pending_acks.get(in_reply_to)
                if event is not None:
                    self._ack_results[in_reply_to] = payload
                    event.set()

        handler = self._handlers.get(msg.topic)
        if handler is not None:
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
