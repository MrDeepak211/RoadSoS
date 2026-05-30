"""
SMS Alert Module
Sends emergency SMS alerts via Twilio API.
Falls back to WhatsApp deep link + clipboard if Twilio not configured.
"""
import os
import json
import urllib.parse

def send_sms_twilio(to_number: str, message: str) -> dict:
    """Send SMS via Twilio REST API"""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    from_number = os.environ.get("TWILIO_PHONE_NUMBER", "")

    if not all([account_sid, auth_token, from_number]):
        return {"success": False, "error": "Twilio not configured", "fallback": True}

    try:
        import requests
        from requests.auth import HTTPBasicAuth

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        response = requests.post(url, data={
            "From": from_number,
            "To": to_number,
            "Body": message
        }, auth=HTTPBasicAuth(account_sid, auth_token), timeout=10)

        data = response.json()
        if response.status_code == 201:
            return {"success": True, "sid": data.get("sid"), "status": data.get("status")}
        else:
            return {"success": False, "error": data.get("message", "Unknown error")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def build_emergency_sms(location: dict, severity_data: dict, trauma_center: dict = None) -> str:
    """Build formatted emergency SMS message"""
    city = location.get("city", "Unknown")
    country = location.get("country", "Unknown")
    lat = location.get("lat", 0)
    lon = location.get("lon", 0)
    severity = severity_data.get("severity", "HIGH") if severity_data else "HIGH"
    injuries = severity_data.get("injuries_detected", []) if severity_data else []
    maps_link = f"https://maps.google.com/?q={lat},{lon}"

    msg_parts = [
        f"🚨 ROAD ACCIDENT SOS — {severity} SEVERITY",
        f"📍 Location: {city}, {country}",
        f"🗺️ Maps: {maps_link}",
    ]

    if injuries:
        msg_parts.append(f"🩺 Injuries: {', '.join(injuries[:3])}")

    if trauma_center:
        msg_parts.append(f"🏥 Nearest Trauma: {trauma_center['name']} ({trauma_center['distance_km']}km)")
        msg_parts.append(f"📞 Hospital: {trauma_center['phone']}")

    msg_parts.append("⚡ PLEASE CALL EMERGENCY SERVICES IMMEDIATELY")
    msg_parts.append("Sent via RoadSoS Emergency App")

    return "\n".join(msg_parts)


def get_whatsapp_link(phone: str, message: str) -> str:
    """Generate WhatsApp deep link for emergency message"""
    clean_phone = phone.replace("+", "").replace("-", "").replace(" ", "")
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{clean_phone}?text={encoded}"


def get_sms_link(phone: str, message: str) -> str:
    """Generate SMS deep link (mobile fallback)"""
    encoded = urllib.parse.quote(message)
    return f"sms:{phone}?body={encoded}"


def send_bulk_alerts(contacts: list, message: str) -> list:
    """Send SMS to multiple emergency contacts"""
    results = []
    for contact in contacts:
        number = contact.get("phone", "")
        name = contact.get("name", "Contact")
        result = send_sms_twilio(number, message)
        result["name"] = name
        result["phone"] = number
        results.append(result)
    return results


def get_sms_config_html():
    """HTML for SMS configuration UI"""
    return """
    <div style="
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 14px; padding: 1.2rem;
        color: white; font-family: sans-serif;
        border: 1px solid rgba(39,174,96,0.3);
    ">
        <h4 style="margin:0 0 0.5rem 0;">📩 SMS Alert System</h4>
        <p style="margin:0; opacity:0.7; font-size:0.83rem;">
            Configure Twilio credentials to enable real SMS alerts.<br>
            Or use WhatsApp/SMS links as instant fallback.
        </p>
        <div style="margin-top:0.8rem; background:rgba(255,255,255,0.05); border-radius:8px; padding:0.7rem; font-size:0.8rem;">
            <b>Setup:</b><br>
            1. Create free account at <a href="https://twilio.com" target="_blank" style="color:#3498db">twilio.com</a><br>
            2. Get Account SID, Auth Token, Phone Number<br>
            3. Set as environment variables:<br>
            <code style="color:#2ecc71">TWILIO_ACCOUNT_SID=xxx</code><br>
            <code style="color:#2ecc71">TWILIO_AUTH_TOKEN=xxx</code><br>
            <code style="color:#2ecc71">TWILIO_PHONE_NUMBER=+1xxx</code>
        </div>
    </div>
    """
