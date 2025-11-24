import re

def detect_language(text: str) -> str:
    """
    Detect language from text
    
    Supported languages:
    - zh-CN: Simplified Chinese
    - zh-TW: Traditional Chinese  
    - es: Spanish
    - fr: French
    - ja: Japanese
    - ko: Korean
    - en: English (default)
    """
    # Check for Chinese characters
    if re.search(r"[\u4e00-\u9fff]", text):
        # Traditional Chinese specific characters (more common in Traditional)
        traditional_chars = r"[\u3400-\u4DBF\uF900-\uFAFF]"
        # Common Traditional Chinese characters not used in Simplified
        traditional_specific = r"[繁體爲與]"
        
        if re.search(traditional_chars, text) or re.search(traditional_specific, text):
            return "zh-TW"  # Traditional Chinese
        else:
            return "zh-CN"  # Simplified Chinese (default for Chinese)
    
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
        "zh-CN": "Simplified Chinese",
        "zh-TW": "Traditional Chinese",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "es": "Spanish",
        "fr": "French",
    }.get(lang, lang)
    return f"[EN][auto from {label}] {text}"
