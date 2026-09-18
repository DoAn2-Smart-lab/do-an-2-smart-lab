"""
Hang so topic MQTT cho Safety & Practical Tutoring Agent.

PHAI khop 100% voi docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (ban chot Ngay 2).
KHONG tu dat ten topic/QoS/retain moi trong file nay - neu can thay doi, sua file .md do truoc,
thong nhat voi nguoi phu trach Master Orchestrator/Lab Data/Power Agent, roi moi cap nhat lai day.
Safety Agent chi can 3/8 topic cua he thong (status/command/alert) nen file nay khong liet ke
5 topic con lai (xem agents/master-orchestrator/app/mqtt/topics.py neu can doi chieu du 8 topic).
"""

TOPIC_SAFETY_STATUS = "lab/safety/status"
TOPIC_SAFETY_COMMAND = "lab/safety/command"  # 2 chieu: request (Orchestrator) + ack (Safety)
TOPIC_SAFETY_ALERT = "lab/safety/alert"

# ---- QoS + retain dung dung bang trong file schema (dung khi publish/subscribe) ----
TOPIC_QOS = {
    TOPIC_SAFETY_STATUS: 1,
    TOPIC_SAFETY_COMMAND: 1,
    TOPIC_SAFETY_ALERT: 2,
}

TOPIC_RETAIN = {
    TOPIC_SAFETY_STATUS: True,
    TOPIC_SAFETY_COMMAND: False,
    TOPIC_SAFETY_ALERT: False,
}

# ---- Topic Safety Agent DUOC PHEP publish ----
# TOPIC_SAFETY_COMMAND: CHI duoc publish message co "type": "ack" (tra loi yeu cau tu
# Orchestrator). TUYET DOI KHONG tu publish "type": "request" - viec do CHI Master Orchestrator
# duoc lam (xem SafetyCommandRequest trong models/schemas.py).
PUBLISH_TOPICS = {
    TOPIC_SAFETY_STATUS,
    TOPIC_SAFETY_COMMAND,
    TOPIC_SAFETY_ALERT,
}

# ---- Topic Safety Agent DUOC PHEP subscribe ----
# Chi subscribe lai TOPIC_SAFETY_COMMAND de nhan "request" tu Orchestrator (bo qua message
# "type": "ack" cua chinh minh vong lai qua handler, xem app/main.py).
SUBSCRIBE_TOPICS = {
    TOPIC_SAFETY_COMMAND,
}
