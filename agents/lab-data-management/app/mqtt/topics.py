"""
Hang so topic MQTT cho Lab Data Management Agent.

PHAI khop 100% voi docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (ban chot Ngay 2).
KHONG tu dat ten topic/QoS/retain moi trong file nay - neu can thay doi, sua file .md do truoc,
thong nhat voi nguoi phu trach Master Orchestrator/Safety/Power Agent, roi moi cap nhat lai day.
Lab Data Agent chi can 2/8 topic cua he thong (query/result) nen file nay khong liet ke 6 topic
con lai (xem agents/master-orchestrator/app/mqtt/topics.py neu can doi chieu du 8 topic).
"""

TOPIC_DATA_QUERY = "lab/data/query"
TOPIC_DATA_RESULT = "lab/data/result"

# ---- QoS + retain dung dung bang trong file schema (dung khi publish/subscribe) ----
TOPIC_QOS = {
    TOPIC_DATA_QUERY: 1,
    TOPIC_DATA_RESULT: 1,
}

TOPIC_RETAIN = {
    TOPIC_DATA_QUERY: False,
    TOPIC_DATA_RESULT: False,
}

# ---- Topic Lab Data Agent DUOC PHEP publish ----
PUBLISH_TOPICS = {
    TOPIC_DATA_RESULT,
}

# ---- Topic Lab Data Agent DUOC PHEP subscribe ----
SUBSCRIBE_TOPICS = {
    TOPIC_DATA_QUERY,
}
