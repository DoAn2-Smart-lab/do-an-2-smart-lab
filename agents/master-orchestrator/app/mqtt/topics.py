"""
Hang so topic MQTT cho Master Orchestrator Agent.

PHAI khop 100% voi docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (ban chot Ngay 2).
KHONG tu dat ten topic/QoS/retain moi trong file nay - neu can thay doi, sua file .md do truoc,
thong nhat voi nguoi phu trach Lab Data + Power Agent, roi moi cap nhat lai day.
"""

# ---- 8 topic, dung thu tu nhu trong file schema ----
TOPIC_ORCHESTRATOR_INTENT = "lab/orchestrator/intent"
TOPIC_SAFETY_STATUS = "lab/safety/status"
TOPIC_SAFETY_COMMAND = "lab/safety/command"  # 2 chieu: request (Orchestrator) + ack (Safety)
TOPIC_SAFETY_ALERT = "lab/safety/alert"
TOPIC_DATA_QUERY = "lab/data/query"
TOPIC_DATA_RESULT = "lab/data/result"
TOPIC_POWER_STATUS = "lab/power/status"
TOPIC_POWER_COMMAND = "lab/power/command"

# ---- QoS + retain dung dung bang trong file schema (dung khi publish/subscribe) ----
TOPIC_QOS = {
    TOPIC_ORCHESTRATOR_INTENT: 1,
    TOPIC_SAFETY_STATUS: 1,
    TOPIC_SAFETY_COMMAND: 1,
    TOPIC_SAFETY_ALERT: 2,
    TOPIC_DATA_QUERY: 1,
    TOPIC_DATA_RESULT: 1,
    TOPIC_POWER_STATUS: 0,
    TOPIC_POWER_COMMAND: 1,
}

TOPIC_RETAIN = {
    TOPIC_ORCHESTRATOR_INTENT: False,
    TOPIC_SAFETY_STATUS: True,
    TOPIC_SAFETY_COMMAND: False,
    TOPIC_SAFETY_ALERT: False,
    TOPIC_DATA_QUERY: False,
    TOPIC_DATA_RESULT: False,
    TOPIC_POWER_STATUS: True,
    TOPIC_POWER_COMMAND: False,
}

# ---- Topic Master Orchestrator DUOC PHEP publish ----
# TOPIC_SAFETY_COMMAND: CHI duoc publish message co "type": "request" (yeu cau Safety Agent
# hanh dong). TUYET DOI KHONG tu publish "type": "ack" hoac lenh dong/cat contactor truc tiep -
# viec do CHI Safety Agent duoc lam (xem SafetyCommandAck trong models/schemas.py va nguyen tac
# "Safety Agent la noi DUY NHAT publish lenh dong/cat contactor xuong PLC" trong file schema).
PUBLISH_TOPICS = {
    TOPIC_ORCHESTRATOR_INTENT,
    TOPIC_SAFETY_COMMAND,
    TOPIC_DATA_QUERY,
    TOPIC_POWER_COMMAND,
}

# ---- Topic Master Orchestrator DUOC PHEP subscribe ----
# TOPIC_SAFETY_COMMAND cung nam trong danh sach subscribe: Orchestrator lang nghe chinh topic
# no vua publish request de nhan lai ACK/NACK (khop qua "in_reply_to" == message_id cua request).
SUBSCRIBE_TOPICS = {
    TOPIC_SAFETY_STATUS,
    TOPIC_SAFETY_COMMAND,
    TOPIC_SAFETY_ALERT,
    TOPIC_DATA_RESULT,
    TOPIC_POWER_STATUS,
}
