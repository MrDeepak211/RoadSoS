COUNTRY_FLAGS = {
    "Bangladesh": "🇧🇩", "Sri Lanka": "🇱🇰",
    "Nepal": "🇳🇵", "Myanmar": "🇲🇲", "Thailand": "🇹🇭", "Bhutan": "🇧🇹"
}

SERVICE_ICONS = {
    "hospital": "🏥", "police": "👮", "ambulance": "🚑", "rescue": "🚒"
}

SEVERITY_COLORS = {
    "CRITICAL": "#c0392b", "HIGH": "#e67e22",
    "MODERATE": "#f39c12", "LOW": "#27ae60"
}

SEVERITY_EMOJIS = {
    "CRITICAL": "🔴", "HIGH": "🟠", "MODERATE": "🟡", "LOW": "🟢"
}

CITY_COORDS = {
    "Pune": (18.5204, 73.8567), "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.6139, 77.2090), "Dhaka": (23.8103, 90.4125),
    "Chittagong": (22.3569, 91.7832), "Colombo": (6.9271, 79.8612),
    "Kathmandu": (27.7172, 85.3240), "Yangon": (16.8409, 96.1735),
    "Bangkok": (13.7563, 100.5018), "Thimphu": (27.4661, 89.6419)
}

CITY_MAP = {
    "Bangladesh": ["Dhaka", "Chittagong"],
    "Sri Lanka": ["Colombo"],
    "Nepal": ["Kathmandu"],
    "Myanmar": ["Yangon"],
    "Thailand": ["Bangkok"],
    "Bhutan": ["Thimphu"]
}

LANGUAGES = {
    "Hindi (हिंदी)": "Hindi",
    "Bengali (বাংলা)": "Bengali",
    "Sinhala (සිංහල)": "Sinhala",
    "Nepali (नेपाली)": "Nepali",
    "Burmese (မြန်မာ)": "Burmese",
    "Thai (ภาษาไทย)": "Thai",
    "Dzongkha (རྫོང་ཁ)": "Dzongkha"
}

QUICK_SCENARIOS = [
    ("🏍️ Bike crash, person down", "Motorcycle accident, rider fell and is injured on the road"),
    ("🚗 Car collision, airbag deployed", "Car accident with airbag deployment, driver conscious but shaken"),
    ("🩸 Heavy bleeding, won't stop", "Severe bleeding from injury that won't stop"),
    ("😵 Person unconscious", "Person is unconscious and not responding after accident"),
    ("👦 Child injured", "Child was injured in road accident"),
    ("🔥 Vehicle on fire", "Vehicle caught fire after accident"),
]

CRASH_KEYWORDS = [
    "accident", "crash", "collision", "hit", "injured", "bleeding",
    "unconscious", "help", "emergency", "sos", "hurt", "trapped", "pain"
]

def detect_crash_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in CRASH_KEYWORDS)

def get_severity_color(severity: str) -> str:
    return SEVERITY_COLORS.get(severity, "#7f8c8d")

def format_eta(minutes: int) -> str:
    if minutes < 60:
        return f"~{minutes} min"
    hours = minutes // 60
    mins = minutes % 60
    return f"~{hours}h {mins}m"
