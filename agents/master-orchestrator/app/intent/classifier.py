"""
Bo phan loai y dinh (Intent Recognition) toi thieu - rule-based keyword matching.

Day la ban skeleton de test luong end-to-end (tieu chi nghiem thu #1 trong de cuong: dinh
tuyen dung toi thieu 4 kich ban lenh khac nhau). Theo
docs-thiet-ke/Tong-hop-y-tuong-Zalo-va-dinh-huong-tiep-theo.md muc 2, giai doan sau se thay
bang SLM local (Qwen2.5-3B-Instruct hoac Llama-3.2-3B-Instruct, quantized 4-bit GGUF qua
Ollama) thay vi rule-based nay.
"""
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional

TargetAgent = Literal["safety_tutoring", "lab_data", "power_load"]

# Tu khoa co chu y tranh trung lap giua cac nhom (vd khong dung "thuc hanh" chung chung cho
# safety_tutoring vi lab_data co "lich thuc hanh"/"ban thuc hanh").
_KEYWORDS: Dict[TargetAgent, List[str]] = {
    "safety_tutoring": [
        "dol", "sao tam giac", "sao - tam giac", "sao – tam giac",
        "khoi dong", "dao chieu", "e-stop", "estop", "cap nguon", "dong nguon",
        "ro-le nhiet", "ngan mach", "contactor",
    ],
    "lab_data": [
        "thiet bi", "lich thuc hanh", "ban thuc hanh", "muon", "tra thiet bi",
        "kiem dinh", "tra cuu",
    ],
    "power_load": [
        "den", "quat", "cong suat", "phu tai", "tiet kiem dien",
    ],
}


@dataclass
class IntentResult:
    target_agent: Optional[TargetAgent]
    intent: str


def classify(text: str) -> IntentResult:
    normalized = _normalize(text)
    for agent, keywords in _KEYWORDS.items():
        if any(_normalize(kw) in normalized for kw in keywords):
            return IntentResult(target_agent=agent, intent=_infer_intent_name(agent, normalized))
    return IntentResult(target_agent=None, intent="unknown")


def _normalize(text: str) -> str:
    # Bo dau tieng Viet de so khop on dinh du nguoi dung go co dau hay khong ("khoi dong"
    # hay "khởi động" deu ra cung 1 chuoi da chuan hoa). "d"/"D" xu ly rieng vi U+0111 (đ)
    # khong tach thanh d + dau qua NFD nhu cac nguyen am co dau khac.
    text = text.lower().replace("đ", "d")
    nfd = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")


def _infer_intent_name(agent: TargetAgent, normalized_text: str) -> str:
    # TODO (Tuan 3-4): tach tham so cu the (ten ban thuc hanh, zone, action) tu cau lenh that,
    # hien tai chi tra ve ten intent chung chung du de route_to_agent chon dung topic.
    if agent == "safety_tutoring":
        if "sao tam giac" in normalized_text or "dao chieu" in normalized_text:
            return "start_star_delta_practice"
        return "start_dol_practice"
    if agent == "lab_data":
        return "query_lab_data"
    return "power_load_command"
