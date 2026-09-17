"""
Test toi thieu cho bo phan loai y dinh - 4 kich ban lenh khac nhau, khop tieu chi nghiem thu
#1 trong de cuong ("dinh tuyen chinh xac den sub-agent tuong ung qua Chat, toi thieu 4 kich
ban lenh khac nhau"). Bo sung Ngay 2: kiem tra ca table_id/action da duoc tach rieng khoi
raw_text (truoc day gop chung trong 1 chuoi "intent" duy nhat).
"""
from app.intent.classifier import classify


def test_classify_safety_tutoring():
    result = classify("Cho tôi thực hành khởi động DOL ở bàn B03")
    assert result.target_agent == "safety_tutoring"
    assert result.table_id == "B03"
    assert result.action == "power_on"


def test_classify_lab_data():
    result = classify("Lịch thực hành bàn B03 hôm nay thế nào?")
    assert result.target_agent == "lab_data"
    assert result.table_id == "B03"
    assert result.action is None


def test_classify_power_load():
    result = classify("Tắt đèn phòng thí nghiệm khu B")
    assert result.target_agent == "power_load"
    assert result.table_id is None
    assert result.action == "turn_off"


def test_classify_unknown():
    result = classify("Hôm nay trời đẹp quá")
    assert result.target_agent is None
    assert result.table_id is None
    assert result.action is None
