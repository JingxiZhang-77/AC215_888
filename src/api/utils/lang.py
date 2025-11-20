import re

def detect_language(text: str) -> str:
    if re.search(r"[\u4e00-\u9fff]", text):
        return "zh"
    if re.search(r"[ぁ-ゟ゠-ヿ]", text):
        return "ja"
    if re.search(r"[가-힣]", text):
        return "ko"
    if re.search(r"[áéíóúñü¿¡]", text.lower()):
        return "es"
    if re.search(r"[àâçéèêëîïôùûüœ]", text.lower()):
        return "fr"
    return "en"

def pseudo_translate(text: str, lang: str) -> str:
    label = {
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "es": "Spanish",
        "fr": "French",
    }.get(lang, lang)
    return f"[EN][auto from {label}] {text}"
