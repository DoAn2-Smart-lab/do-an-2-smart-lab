"""
Hang so topic MQTT cho Master Orchestrator Agent.

PHAI khop 100% voi docs-thiet-ke/Thiet-ke-Event-Bus-MQTT-Topic-Schema.md (ban nhap Tuan 2).
KHONG tu dat ten topic moi trong file nay — neu can topic/field moi, sua file .md do truoc,
thong nhat voi nguoi phu trach Lab Data + Power Agent, roi moi cap nhat lai day.
"""

# ---- Topic Master Orchestrator DUOC PHEP publish ----
TOPIC_ORCHESTRATOR_INTENT = "lab/orchestrator/intent"  # -> Safety / LabData / Power Agent
TOPIC_DATA_QUERY = "lab/data/query"                     # -> Lab Data Management Agent
TOPIC_POWER_COMMAND = "lab/power/command"               # -> Power & Load Management Agent

# ---- Topic Master Orchestrator DUOC PHEP subscribe ----
TOPIC_SAFETY_STATUS = "lab/safety/status"  # <- Safety Agent
TOPIC_SAFETY_ALERT = "lab/safety/alert"    # <- Safety Agent, Telegram bridge
TOPIC_DATA_RESULT = "lab/data/result"      # <- Lab Data Management Agent
TOPIC_POWER_STATUS = "lab/power/status"    # <- Power & Load Management Agent

# ---- TUYET DOI KHONG publish topic nay tu Master Orchestrator ----
# "lab/safety/command" - CHI Safety Agent duoc publish (dong/cat contactor). Nguyen tac ghi
# ro trong file schema: "Master Orchestrator KHONG dieu khien PLC truc tiep — moi lenh lien
# quan an toan phai di qua topic cua Safety Agent, Safety Agent la noi DUY NHAT publish lenh
# dong/cat contactor."

PUBLISH_TOPICS = {
    TOPIC_ORCHESTRATOR_INTENT,
    TOPIC_DATA_QUERY,
    TOPIC_POWER_COMMAND,
}

SUBSCRIBE_TOPICS = {
    TOPIC_SAFETY_STATUS,
    TOPIC_SAFETY_ALERT,
    TOPIC_DATA_RESULT,
    TOPIC_POWER_STATUS,
}
