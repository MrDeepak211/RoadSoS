import requests
import json
import os

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01"
}

# ─── System Prompts ────────────────────────────────────────────────────────
CHAT_SYSTEM = """You are RoadSoS, an AI emergency assistant for road accidents across BIMSTEC countries (Bangladesh, Sri Lanka, Nepal, Myanmar, Thailand, Bhutan).

RULES:
- Be CALM, CLEAR, SHORT — accident victims are in panic
- Always tell them to call emergency services FIRST
- Give step-by-step actionable guidance
- Be warm and reassuring
- Use simple language (not complex medical jargon)
- If life-threatening: prioritize CPR, bleeding control, airway
- Always mention country-specific emergency numbers when relevant

Bangladesh: Emergency 999
Sri Lanka: Ambulance 1990 | Police 119
Nepal: Ambulance 102 | Police 100
Myanmar: Ambulance 192 | Police 199
Thailand: EMS 1669 | Police 191
Bhutan: Ambulance 112 | Police 113"""

SEVERITY_SYSTEM = """You are an emergency triage AI. Analyze accident descriptions and return ONLY valid JSON.

Classify severity as: CRITICAL, HIGH, MODERATE, LOW

Return exactly this JSON structure:
{
  "severity": "CRITICAL|HIGH|MODERATE|LOW",
  "severity_score": 1-10,
  "incident_type": "vehicle_collision|pedestrian|motorcycle|fall|other",
  "injuries_detected": ["list of detected injuries"],
  "immediate_actions": ["top 3 immediate actions"],
  "services_needed": ["ambulance", "police", "trauma_center", "fire", "towing"],
  "golden_hour_risk": true/false,
  "reasoning": "brief explanation"
}"""

TRANSLATE_SYSTEM = """You are an emergency multilingual translator for road accidents.
Translate the emergency message to the target language clearly and concisely.
Keep it SHORT — it's for emergency use.
Return ONLY the translated text, nothing else."""

FIRSTAID_SYSTEM = """You are a first aid AI expert. Generate clear, numbered first aid steps for the given situation.
Return ONLY a JSON array of steps like:
["Step 1: ...", "Step 2: ...", "Step 3: ..."]
Maximum 6 steps. Simple language. Life-saving focus."""

def call_claude(system_prompt, user_message, max_tokens=800):
    """Core API call with proper headers"""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=HEADERS,
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}]
            },
            timeout=20
        )
        data = response.json()
        if "content" in data:
            return data["content"][0]["text"]
        return None
    except Exception as e:
        return None

def call_claude_with_history(messages, system_prompt=CHAT_SYSTEM, max_tokens=600):
    """Chat with conversation history"""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=HEADERS,
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": messages
            },
            timeout=20
        )
        data = response.json()
        if "content" in data:
            return data["content"][0]["text"]
        return None
    except Exception:
        return None

def analyze_severity(incident_text: str) -> dict:
    """AI Accident Severity Detection — Core Innovation Feature"""
    result = call_claude(SEVERITY_SYSTEM, incident_text, max_tokens=600)
    if result:
        try:
            clean = result.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except:
            pass
    # Offline fallback
    text_lower = incident_text.lower()
    if any(w in text_lower for w in ["unconscious","not breathing","critical","heavy bleeding","trapped"]):
        sev = "CRITICAL"; score = 9
    elif any(w in text_lower for w in ["bleeding","broken","fracture","head injury","chest"]):
        sev = "HIGH"; score = 7
    elif any(w in text_lower for w in ["pain","injury","hurt","accident","crash"]):
        sev = "MODERATE"; score = 5
    else:
        sev = "LOW"; score = 3

    return {
        "severity": sev, "severity_score": score,
        "incident_type": "vehicle_collision",
        "injuries_detected": ["injury detected"],
        "immediate_actions": ["Call ambulance immediately", "Keep victim still", "Apply pressure to wounds"],
        "services_needed": ["ambulance", "police"],
        "golden_hour_risk": score >= 7,
        "reasoning": "Offline analysis based on keywords"
    }

def get_golden_hour_analysis(incident_text: str, trauma_center: dict, severity_data: dict) -> str:
    """Golden Hour AI — The Killer Feature"""
    if not trauma_center:
        return "⚠️ No trauma center data available. Call 108 immediately!"

    eta = trauma_center.get("eta_minutes", 30)
    dist = trauma_center.get("distance_km", 10)
    severity = severity_data.get("severity", "HIGH")
    score = severity_data.get("severity_score", 7)

    prompt = f"""
Accident: {incident_text}
Severity: {severity} (score {score}/10)
Nearest Trauma Center: {trauma_center['name']}
Distance: {dist} km
Estimated ETA: {eta} minutes
Golden Hour Risk: {severity_data.get('golden_hour_risk', True)}

Generate a SHORT Golden Hour analysis (3-4 sentences max):
1. Is the patient within the golden hour window?
2. What is the critical action in the next 5 minutes?
3. What should bystanders do while waiting?
Be direct and urgent but calm."""

    result = call_claude(CHAT_SYSTEM, prompt, max_tokens=300)
    if result:
        return result

    # Offline fallback
    if eta <= 15:
        return f"✅ Trauma center is {dist}km away (~{eta} min). You're within the golden hour window. Keep victim stable, apply pressure to wounds, and stay on the line with emergency services."
    elif eta <= 45:
        return f"⚠️ Trauma center is {dist}km away (~{eta} min). Time is critical — call ambulance NOW (108/1669/1990). Do not move the victim unless in danger. Control bleeding immediately."
    else:
        return f"🚨 CRITICAL: Nearest trauma center is {dist}km away (~{eta} min). Every second counts! Call ambulance IMMEDIATELY. Begin CPR if victim is unresponsive. Do not wait."

def translate_emergency(text: str, target_language: str) -> str:
    """Multilingual Emergency Translation"""
    prompt = f"Translate this emergency message to {target_language}:\n\n{text}"
    result = call_claude(TRANSLATE_SYSTEM, prompt, max_tokens=300)
    return result if result else f"[Translation unavailable — {target_language}]\n{text}"

def generate_first_aid_steps(situation: str) -> list:
    """AI-Generated First Aid Steps"""
    result = call_claude(FIRSTAID_SYSTEM, situation, max_tokens=400)
    if result:
        try:
            clean = result.strip()
            if "```" in clean:
                clean = clean.split("```")[1]
                if clean.startswith("json"):
                    clean = clean[4:]
            return json.loads(clean.strip())
        except:
            pass
    # Fallback
    situation_lower = situation.lower()
    if "bleed" in situation_lower:
        return ["Apply firm pressure with clean cloth","Do NOT remove cloth — add more on top","Elevate limb above heart if possible","Keep victim warm and calm","Call 108/ambulance immediately","Stay with victim until help arrives"]
    elif "cpr" in situation_lower or "breathing" in situation_lower or "unconscious" in situation_lower:
        return ["Call ambulance FIRST (108/1669/1990)","Tilt head back, lift chin","Check for breathing (10 seconds)","30 chest compressions — hard and fast","2 rescue breaths","Repeat until ambulance arrives"]
    else:
        return ["Call emergency services immediately","Do NOT move victim unless in danger","Keep victim warm and conscious","Apply pressure to any visible wounds","Note victim's condition for paramedics","Stay calm and stay with the victim"]

def chat_response(messages: list, user_message: str, location: dict) -> str:
    """Main chatbot with location context"""
    location_ctx = f"[User location: {location.get('city','Unknown')}, {location.get('country','Unknown')}]"
    enriched = messages + [{"role": "user", "content": f"{location_ctx} {user_message}"}]
    result = call_claude_with_history(enriched)
    if result:
        return result
    # Offline fallback
    country = location.get("country", "Nepal")
    fallback_numbers = {
        "Bangladesh": "999 (Emergency)",
        "Sri Lanka": "1990 (Ambulance) | 119 (Police)",
        "Nepal": "102 (Ambulance) | 100 (Police)",
        "Myanmar": "192 (Ambulance) | 199 (Police)",
        "Thailand": "1669 (EMS) | 191 (Police)",
        "Bhutan": "112 (Ambulance) | 113 (Police)"
    }
    return f"⚠️ AI offline. Call emergency services NOW:\n📞 {fallback_numbers.get(country, '102 / 999 / 119')}\n\nStay calm. Keep victim still. Apply pressure to wounds."
