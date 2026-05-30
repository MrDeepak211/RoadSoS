# ═══════════════════════════════════════════════════
# RoadSoS v3.0 — AI Emergency Road Safety Assistant
# Team: Night Wolfpack
# Members: Deepak Tandale (Leader), Krushna Ingole,
#           Ritesh Ghogare, Neha Kadas
# Institution: SSIEMS, Maharashtra
# Hackathon: Road Safety Hackathon 2026
#            CoERS, RBG Labs, IIT Madras
# ═══════════════════════════════════════════════════
import streamlit as st
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))

from modules.database import (init_db, get_nearby_services, get_nearest_trauma_center,
                               get_emergency_numbers, log_incident, get_analytics)
from modules.ai_assistant import (analyze_severity, get_golden_hour_analysis,
                                   translate_emergency, generate_first_aid_steps, chat_response)
from modules.utils import *
from modules.voice_sos import get_voice_component_html
from modules.live_map import build_emergency_map, get_gps_html
from modules.auto_emergency import get_auto_emergency_html
from modules.sms_alert import (build_emergency_sms, send_sms_twilio,
                                get_whatsapp_link, get_sms_link, send_bulk_alerts)

st.set_page_config(
    page_title="RoadSoS v3.0 | Night Wolfpack",
    page_icon="🚨", layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');
*, html, body { font-family: 'DM Sans', sans-serif; }

.hero { background:linear-gradient(135deg,#8C1010,#C02020,#8C1010);
    padding:1.5rem 2rem; border-radius:16px; color:white; margin-bottom:1rem; }
.hero h1 { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; margin:0; }
.hero p  { opacity:0.85; margin:0.2rem 0 0.6rem; font-size:0.95rem; }
.badge { background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.3);
    color:white; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:600;
    margin-right:5px; display:inline-block; }
.badge-green { background:rgba(39,174,96,0.4); border:1px solid rgba(39,174,96,0.6);
    color:#afffcb; padding:3px 10px; border-radius:20px; font-size:0.72rem;
    font-weight:600; margin-right:5px; display:inline-block; }

/* AI STATUS BANNER */
.ai-running { background:linear-gradient(90deg,#1a1a2e,#16213e);
    color:white; border-radius:10px; padding:0.7rem 1.2rem; margin:0.5rem 0;
    border-left:4px solid #e74c3c; font-size:0.88rem; }
.ai-done { background:linear-gradient(90deg,#0d2e1a,#0d3320);
    color:white; border-radius:10px; padding:0.7rem 1.2rem; margin:0.5rem 0;
    border-left:4px solid #27ae60; font-size:0.88rem; }

/* SEVERITY */
.sev-critical { background:linear-gradient(135deg,#c0392b,#922b21); color:white;
    border-radius:14px; padding:1.2rem 1.5rem; margin:0.6rem 0; position:relative; }
.sev-high     { background:linear-gradient(135deg,#e67e22,#ca6f1e); color:white;
    border-radius:14px; padding:1.2rem 1.5rem; margin:0.6rem 0; position:relative; }
.sev-moderate { background:linear-gradient(135deg,#d4ac0d,#b7950b); color:white;
    border-radius:14px; padding:1.2rem 1.5rem; margin:0.6rem 0; position:relative; }
.sev-low      { background:linear-gradient(135deg,#27ae60,#1e8449); color:white;
    border-radius:14px; padding:1.2rem 1.5rem; margin:0.6rem 0; position:relative; }
.sev-score { position:absolute; top:1rem; right:1.2rem;
    font-family:'Syne',sans-serif; font-size:2.5rem; font-weight:800; opacity:0.25; }

/* GOLDEN HOUR */
.golden { background:linear-gradient(135deg,#b7770d,#d4ac0d); color:white;
    border-radius:14px; padding:1rem 1.4rem; margin:0.6rem 0; }
.golden h4 { margin:0 0 0.4rem; font-family:'Syne',sans-serif; font-size:1rem; }

/* SERVICES */
.svc { background:white; border-radius:12px; padding:0.8rem 1rem; margin:0.4rem 0;
    border-left:4px solid #e74c3c; box-shadow:0 2px 8px rgba(0,0,0,0.07); }
.svc h4 { margin:0 0 0.15rem; font-size:0.85rem; font-weight:600; color:#1a1a2e; }
.svc p  { margin:0; font-size:0.76rem; color:#666; }
.tag-red  { background:#e74c3c; color:white; padding:2px 7px;
    border-radius:20px; font-size:0.68rem; font-weight:600; float:right; }
.tag-dark { background:#2c3e50; color:white; padding:2px 7px;
    border-radius:20px; font-size:0.68rem; float:right; margin-right:3px; }

/* FIRST AID */
.step { display:flex; gap:0.7rem; align-items:flex-start; background:#fff5f5;
    border-radius:10px; padding:0.6rem 0.9rem; margin:0.25rem 0; border:1px solid #fde8e8; }
.step-n { width:24px; height:24px; border-radius:50%; background:#e74c3c;
    color:white; display:flex; align-items:center; justify-content:center;
    font-size:0.72rem; font-weight:700; flex-shrink:0; }

/* CHAT */
.chat-user { background:linear-gradient(135deg,#e74c3c,#c0392b); color:white;
    padding:0.7rem 1rem; border-radius:16px 16px 4px 16px; margin:0.3rem 0 0.3rem auto;
    max-width:80%; font-size:0.88rem; line-height:1.55; }
.chat-bot  { background:#f1f3f5; color:#1a1a2e;
    padding:0.7rem 1rem; border-radius:16px 16px 16px 4px; margin:0.3rem auto 0.3rem 0;
    max-width:85%; font-size:0.88rem; line-height:1.55; border:1px solid #e9ecef; }

/* STAT */
.stat { background:#1a1a2e; color:white; border-radius:12px;
    padding:0.9rem; text-align:center; }
.stat .n { font-family:'Syne',sans-serif; font-size:1.7rem;
    font-weight:800; color:#e74c3c; display:block; }
.stat .l { font-size:0.65rem; opacity:0.55; text-transform:uppercase; letter-spacing:0.5px; }

/* CRASH FLASH */
.crash { background:linear-gradient(135deg,#c0392b,#922b21); color:white;
    border-radius:14px; padding:1rem 1.5rem; margin:0.5rem 0;
    animation:flash 0.8s ease-in-out 5; }
@keyframes flash { 0%,100%{opacity:1} 50%{opacity:0.5} }

/* SMS */
.sms-card { background:linear-gradient(135deg,#1a1a2e,#0d3349); color:white;
    border-radius:14px; padding:1rem 1.2rem; margin:0.4rem 0;
    border:1px solid rgba(39,174,96,0.3); }
</style>
""", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────────────────
init_db()
DEFAULTS = {
    "messages": [], "sev": None, "golden": None, "trauma": None,
    "aid_steps": [], "nearby": [], "coords": (27.7172,85.3240),
    "country": "Nepal", "city": "Kathmandu",
    "gps_lat": None, "gps_lon": None,
    "contacts": [{"name":"Emergency Contact 1","phone":""}],
    "sms_results": [], "translated": "",
    "last_input": "", "ai_processing": False,
    "auto_ran": False,
}
for k,v in DEFAULTS.items():
    if k not in st.session_state: st.session_state[k] = v

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🚨 RoadSoS v3.0</h1>
  <p>Fully Automatic AI Emergency Road Safety Assistant · BIMSTEC Countries · Night Wolfpack</p>
  <span class="badge">🤖 Auto AI Severity</span>
  <span class="badge">⏱ Golden Hour AI</span>
  <span class="badge-green">🎤 Voice SOS</span>
  <span class="badge-green">🗺 Live GPS Map</span>
  <span class="badge-green">📲 Auto SMS</span>
  <span class="badge">🌐 7 Languages</span>
  <span class="badge">🔌 Offline Ready</span>
</div>
""", unsafe_allow_html=True)

# ── STATS ─────────────────────────────────────────────────────────────────────
analytics = get_analytics()
for col,num,lbl in zip(st.columns(6),
    ["6","37+","24/7",str(analytics["total"]),"6","⚡"],
    ["Countries","Services","AI Support","Incidents","AI Features","Offline"]):
    with col:
        st.markdown(f'<div class="stat"><span class="n">{num}</span><span class="l">{lbl}</span></div>',
            unsafe_allow_html=True)
st.markdown("<br>",unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📍 Location")
    country = st.selectbox("Country", list(COUNTRY_FLAGS.keys()),
        index=list(COUNTRY_FLAGS.keys()).index(st.session_state.country))
    city = st.selectbox("City", CITY_MAP.get(country,["Capital"]))
    coords = CITY_MAP and CITY_COORDS.get(city,(27.7172,85.3240))
    if st.session_state.gps_lat and st.session_state.gps_lon:
        if st.checkbox("Use GPS",value=True):
            coords=(st.session_state.gps_lat,st.session_state.gps_lon)
            st.success(f"📡 {coords[0]:.4f}, {coords[1]:.4f}")
    st.session_state.coords=coords
    st.session_state.country=country
    st.session_state.city=city
    loc={"lat":coords[0],"lon":coords[1],"city":city,"country":country}

    st.markdown("---")
    st.markdown("### ☎️ Emergency Numbers")
    for svc,num in get_emergency_numbers(country):
        st.markdown(f"**{num}** — {svc}")

    st.markdown("---")
    st.markdown("### 🌐 Auto Translate")
    lang_choice=st.selectbox("Language:",list(LANGUAGES.keys()))
    translate_input=st.text_area("Message:",height=65)
    if translate_input:
        with st.spinner("Translating..."):
            translated=translate_emergency(translate_input, LANGUAGES[lang_choice])
            st.info(translated)

# ── FULLY AUTOMATIC AI ENGINE ─────────────────────────────────────────────────
def run_full_ai(text, coords, loc):
    """Runs ALL AI features automatically — no button needed"""
    st.session_state.ai_processing = True

    # 1. Severity Detection
    sev = analyze_severity(text)
    st.session_state.sev = sev

    # 2. Nearest services
    nearby = get_nearby_services(coords[0], coords[1], limit=6)
    st.session_state.nearby = nearby

    # 3. Golden Hour Analysis
    trauma = get_nearest_trauma_center(coords[0], coords[1])
    golden = get_golden_hour_analysis(text, trauma, sev)
    st.session_state.golden = golden
    st.session_state.trauma = trauma

    # 4. First Aid Steps — auto generated
    aid = generate_first_aid_steps(text)
    st.session_state.aid_steps = aid

    # 5. AI Chat — auto response
    reply = chat_response([], text, loc)
    st.session_state.messages = [
        {"role":"user","content":text},
        {"role":"assistant","content": reply or "🤖 Analyzing your emergency..."}
    ]

    # 6. Log incident
    log_incident(country, city, sev["severity"],
        sev.get("incident_type","unknown"), ", ".join(sev.get("services_needed",[])))

    st.session_state.ai_processing = False
    st.session_state.auto_ran = True
    st.session_state.last_input = text

# ── TABS ──────────────────────────────────────────────────────────────────────
tab0,tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
    "🚨 AUTO SOS","🆘 Emergency","🎤 Voice SOS","🗺️ Live Map","📩 SMS Alerts","🤖 AI Chat","📊 Analytics"
])


# TAB 0 — AUTO SOS
with tab0:
    st.markdown("### 🚨 Auto SOS — Camera + Mic + GPS + Live Location")
    st.markdown("**How it works:** Front camera scans every 4s for blood/smoke/fire. Mic listens for help/accident/crash. GPS tracks live. On detection → 5s countdown → auto-sends SOS to police, hospital and all contacts with live location.")
    contacts_for_js = st.session_state.get("contacts",[{"name":"Emergency Contact","phone":""}])
    emergency_nums = get_emergency_numbers(country)
    html_content = get_auto_emergency_html(
        country=country, city=city, lat=coords[0], lon=coords[1],
        contacts=contacts_for_js, emergency_numbers=emergency_nums
    )
    st.components.v1.html(html_content, height=850, scrolling=True)
    st.info("Tip: Add your emergency contacts in the SMS Alerts tab first, then click START here!")

# ══════════════════════════════════════════════
# TAB 1 — FULLY AUTOMATIC EMERGENCY
# ══════════════════════════════════════════════
with tab1:
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown("### ⚡ AI Emergency Analyzer")
        st.markdown(
            "<small style='color:#888'>🤖 <b>Fully Automatic</b> — type or click a scenario, AI instantly analyzes everything</small>",
            unsafe_allow_html=True)

        # ── INPUT ──
        incident = st.text_area(
            "Describe the accident:",
            height=95,
            key="incident_box",
            placeholder="e.g. Bike crash near highway, rider unconscious and bleeding heavily..."
        )

        # ── QUICK SCENARIO BUTTONS — each auto-triggers full AI ──
        st.markdown("**⚡ Quick Scenarios — Auto-AI on Click:**")
        qcols = st.columns(3)
        for i,(label,scenario) in enumerate(QUICK_SCENARIOS):
            with qcols[i%3]:
                if st.button(label, use_container_width=True, key=f"qs_{i}"):
                    with st.spinner(f"🤖 AI running full analysis..."):
                        run_full_ai(scenario, coords, loc)
                    st.rerun()

        # ── MAIN BUTTONS ──
        b1,b2,b3 = st.columns([2,1,1])
        with b1:
            if st.button("🔍 Analyze Now — Full AI", use_container_width=True, type="primary"):
                if incident:
                    with st.spinner("🤖 AI analyzing severity · golden hour · first aid · chat..."):
                        run_full_ai(incident, coords, loc)
                    st.rerun()
                else:
                    st.warning("Please describe the accident first!")
        with b2:
            if st.button("🆘 SOS NOW", use_container_width=True):
                sos_text = f"🆘 SOS EMERGENCY in {city}, {country}! Need immediate help!"
                with st.spinner("🚨 Triggering full SOS AI response..."):
                    run_full_ai(sos_text, coords, loc)
                st.rerun()
        with b3:
            if st.button("🔄 Reset", use_container_width=True):
                for k in ["sev","golden","trauma","aid_steps","messages","nearby","auto_ran","last_input"]:
                    st.session_state[k] = DEFAULTS[k]
                st.rerun()

        # ── AI STATUS ──
        if st.session_state.auto_ran and st.session_state.sev:
            st.markdown('<div class="ai-done">✅ AI Analysis Complete — All 6 features ran automatically</div>',
                unsafe_allow_html=True)

        # ══ AUTO RESULTS — shown immediately ══
        if st.session_state.sev:
            sev = st.session_state.sev
            sev_key = sev["severity"].lower()
            score = sev.get("severity_score",5)
            color_cls = f"sev-{sev_key}"
            emoji = SEVERITY_EMOJIS.get(sev["severity"],"⚠️")

            # Severity Card
            st.markdown(f"""
            <div class="{color_cls}">
                <div class="sev-score">{score}</div>
                <h3 style="margin:0 0 0.3rem;font-family:'Syne',sans-serif">
                    {emoji} {sev['severity']} SEVERITY
                </h3>
                <div style="opacity:0.9;font-size:0.85rem">
                    🔎 {sev.get('reasoning','AI analysis complete')}<br>
                    🩺 {', '.join(sev.get('injuries_detected',['Not specified']))}
                </div>
                <div style="margin-top:0.6rem;font-size:0.82rem;opacity:0.85">
                    ⚡ Score: {score}/10 &nbsp;|&nbsp;
                    🚨 Services: {', '.join(sev.get('services_needed',['ambulance']))} &nbsp;|&nbsp;
                    ⏱ Golden Hour Risk: {"YES ⚠️" if sev.get('golden_hour_risk') else "LOW ✓"}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Immediate Actions
            actions = sev.get("immediate_actions",[])
            if actions:
                st.markdown("**🚨 AI Immediate Actions:**")
                for i,a in enumerate(actions,1):
                    st.markdown(f'<div class="step"><div class="step-n">{i}</div><div>{a}</div></div>',
                        unsafe_allow_html=True)

            # Golden Hour
            if st.session_state.golden:
                st.markdown(f'<div class="golden"><h4>⏱ Golden Hour AI Analysis</h4>{st.session_state.golden}</div>',
                    unsafe_allow_html=True)

            # First Aid — auto generated
            if st.session_state.aid_steps:
                st.markdown("**🩹 AI-Generated First Aid Steps:**")
                for i,step in enumerate(st.session_state.aid_steps,1):
                    st.markdown(f'<div class="step"><div class="step-n">{i}</div><div>{step}</div></div>',
                        unsafe_allow_html=True)

    # Right — services auto-loaded
    with right:
        st.markdown("### 🏥 Auto-Detected Nearby Services")

        # Auto-load nearby services always
        nearby = get_nearby_services(coords[0], coords[1], limit=6)
        for s in nearby:
            icon = SERVICE_ICONS.get(s["type"],"📍")
            tb = " ⭐" if s.get("trauma_level")==1 else ""
            st.markdown(f"""
            <div class="svc">
                <span class="tag-red">{s['distance_km']}km</span>
                <span class="tag-dark">{format_eta(s['eta_minutes'])}</span>
                <h4>{icon} {s['name']}{tb}</h4>
                <p>📞 {s['phone']} · {s.get('address','')}</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ☎️ Emergency Numbers")
        for svc,num in get_emergency_numbers(country):
            st.markdown(f"**📞 {num}** — {svc}")

        # Auto Google Maps link
        st.markdown("---")
        gmaps=f"https://www.google.com/maps/search/hospital/@{coords[0]},{coords[1]},14z"
        st.link_button("📍 Nearest Hospitals on Google Maps", gmaps, use_container_width=True)
        st.link_button("🗺️ View on OpenStreetMap",
            f"https://www.openstreetmap.org/?mlat={coords[0]}&mlon={coords[1]}#map=15/{coords[0]}/{coords[1]}",
            use_container_width=True)

# ══════════════════════════════════════════════
# TAB 2 — VOICE SOS
# ══════════════════════════════════════════════
with tab2:
    st.markdown("### 🎤 Voice SOS — Speak to Trigger AI")
    st.markdown("*Speak any crash keyword — AI auto-detects and runs full analysis*")
    st.markdown('<div class="crash">🎤 VOICE SOS ACTIVE — Say "accident", "crash", "help", "bleeding" to trigger AI automatically</div>',
        unsafe_allow_html=True)
    st.components.v1.html(get_voice_component_html(), height=280, scrolling=False)

    st.markdown("**Crash Keywords that Auto-Trigger AI:**")
    kw_cols = st.columns(4)
    for i,kw in enumerate(CRASH_KEYWORDS[:8]):
        with kw_cols[i%4]:
            st.markdown(f"`{kw}`")

# ══════════════════════════════════════════════
# TAB 3 — LIVE MAP (auto-loads)
# ══════════════════════════════════════════════
with tab3:
    st.markdown("### 🗺️ Live Map — Auto-Loaded")
    mcol1, mcol2 = st.columns([1.4,0.6], gap="large")
    with mcol1:
        st.components.v1.html(get_gps_html(), height=160, scrolling=False)
        nearby_map = get_nearby_services(coords[0],coords[1],limit=10)
        sev_for_map = st.session_state.sev.get("severity") if st.session_state.sev else None
        try:
            import folium
            from streamlit_folium import st_folium
            fmap = build_emergency_map(coords[0],coords[1],nearby_map,sev_for_map,13)
            if fmap:
                st_folium(fmap, width=700, height=420, returned_objects=[])
        except ImportError:
            lat,lon=coords
            osm=f"https://www.openstreetmap.org/export/embed.html?bbox={lon-0.05},{lat-0.05},{lon+0.05},{lat+0.05}&layer=mapnik&marker={lat},{lon}"
            st.markdown(f'<div style="border-radius:14px;overflow:hidden;border:2px solid #e74c3c"><iframe src="{osm}" width="100%" height="420" frameborder="0"></iframe></div>',
                unsafe_allow_html=True)
    with mcol2:
        st.markdown(f"#### {COUNTRY_FLAGS.get(country,'🌏')} {city}, {country}")
        st.markdown(f"`{coords[0]:.4f}°N, {coords[1]:.4f}°E`")
        st.markdown("#### 📍 Nearby Services")
        for s in nearby_map[:5]:
            st.markdown(f"""<div class="svc" style="padding:0.6rem 0.8rem">
                <span class="tag-red">{s['distance_km']}km</span>
                <h4 style="font-size:0.8rem">{SERVICE_ICONS.get(s['type'],'📍')} {s['name']}</h4>
                <p>📞 {s['phone']}</p></div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 4 — SMS ALERTS (auto-builds message)
# ══════════════════════════════════════════════
with tab4:
    st.markdown("### 📩 Auto SMS Alert System")
    scol1,scol2 = st.columns([1.1,0.9],gap="large")
    with scol1:
        st.markdown("#### 👥 Emergency Contacts")
        contacts=st.session_state.contacts
        updated=[]
        for i,c in enumerate(contacts):
            cc1,cc2,cc3=st.columns([2,2,0.5])
            with cc1: nm=st.text_input(f"Name {i+1}",value=c.get("name",""),key=f"cn_{i}",label_visibility="collapsed",placeholder=f"Name {i+1}")
            with cc2: ph=st.text_input(f"Phone {i+1}",value=c.get("phone",""),key=f"cp_{i}",label_visibility="collapsed",placeholder="+977XXXXXXXXX")
            with cc3:
                if st.button("🗑️",key=f"cd_{i}") and len(contacts)>1: continue
            updated.append({"name":nm,"phone":ph})
        st.session_state.contacts=updated
        if st.button("➕ Add Contact",use_container_width=True):
            st.session_state.contacts.append({"name":f"Contact {len(st.session_state.contacts)+1}","phone":""})
            st.rerun()

        # Auto-build SMS from AI results
        sev_for_sms = st.session_state.sev or {"severity":"HIGH","injuries_detected":[],"golden_hour_risk":True}
        sms_msg = build_emergency_sms(loc, sev_for_sms, st.session_state.trauma)
        st.markdown("#### 📝 Auto-Generated Emergency Message")
        st.text_area("SMS Preview (auto-updated from AI):", value=sms_msg, height=180, key="sms_prev")

        s1,s2=st.columns(2)
        with s1:
            if st.button("📩 Send via Twilio",use_container_width=True,type="primary"):
                valid=[c for c in st.session_state.contacts if c.get("phone","").strip()]
                if not valid: st.warning("Add at least one phone number!")
                else:
                    with st.spinner("Sending..."):
                        results=send_bulk_alerts(valid,sms_msg)
                    for r in results:
                        if r.get("success"): st.success(f"✅ Sent to {r['name']}")
                        elif r.get("fallback"): st.warning("⚠️ Twilio not configured — use WhatsApp below")
                        else: st.error(f"❌ Failed: {r.get('error','')}")
        with s2:
            if st.button("🟢 WhatsApp",use_container_width=True):
                for c in [c for c in st.session_state.contacts if c.get("phone","").strip()]:
                    st.link_button(f"📲 {c['name']}",get_whatsapp_link(c["phone"],sms_msg))

    with scol2:
        st.markdown("#### ⚙️ Twilio Setup")
        st.markdown("""<div class="sms-card"><h4>📩 Real SMS via Twilio</h4>
        <div style="background:rgba(255,255,255,0.06);border-radius:8px;padding:0.7rem;font-size:0.76rem;font-family:monospace">
        export TWILIO_ACCOUNT_SID=ACxxx<br>export TWILIO_AUTH_TOKEN=xxx<br>export TWILIO_PHONE_NUMBER=+1xxx
        </div></div>""", unsafe_allow_html=True)
        st.markdown("#### 📋 What Gets Auto-Sent")
        st.markdown("""<div style="background:#f8f9fa;border-radius:12px;padding:0.9rem;font-size:0.82rem">
        ✅ AI severity level<br>✅ GPS location + Maps link<br>✅ Detected injuries<br>
        ✅ Nearest trauma center<br>✅ Emergency numbers<br>✅ Timestamp</div>""",
        unsafe_allow_html=True)
        st.link_button("📍 Your Location on Maps",
            f"https://maps.google.com/?q={coords[0]},{coords[1]}",use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — FULLY AUTO AI CHAT
# ══════════════════════════════════════════════
with tab5:
    st.markdown("### 🤖 RoadSoS AI Chat — Fully Automatic")

    # Auto-load greeting on first visit
    if not st.session_state.messages:
        with st.spinner("🤖 AI loading..."):
            greeting = chat_response([],
                f"You are RoadSoS AI. Give a short 2-line welcome to a user in {city}, {country}. Tell them what you can help with in an emergency.",
                loc)
        st.session_state.messages = [{"role":"assistant",
            "content": greeting or f"👋 Hi! I'm RoadSoS AI. I'm ready to help with any road emergency in {city}, {country}. Describe your situation and I'll instantly guide you!"}]

    # Show chat history
    for msg in st.session_state.messages[-12:]:
        css = "chat-user" if msg["role"]=="user" else "chat-bot"
        icon = "🧑" if msg["role"]=="user" else "🤖"
        st.markdown(f'<div class="{css}">{icon} {msg["content"]}</div>', unsafe_allow_html=True)

    # Auto-suggested quick questions
    st.markdown("**💬 Quick Questions — Auto-AI Response:**")
    qc=st.columns(3)
    QUICK_QS=["What to do if not breathing?","Control heavy bleeding?","Person trapped in car?",
               "Signs of head injury?","Help fracture victim?","Ambulance is 30 min away?"]
    for i,q in enumerate(QUICK_QS):
        with qc[i%3]:
            if st.button(q,key=f"qq_{i}",use_container_width=True):
                st.session_state.messages.append({"role":"user","content":q})
                with st.spinner("🤖 AI responding..."):
                    r=chat_response(st.session_state.messages[:-1],q,loc)
                st.session_state.messages.append({"role":"assistant","content":r})
                st.rerun()

    # Chat input — auto-sends and gets AI response
    with st.form("chat_f",clear_on_submit=True):
        c1,c2,c3=st.columns([5,1,1])
        with c1: umsg=st.text_input("Ask anything...",label_visibility="collapsed",placeholder="Describe situation or ask for help...")
        with c2: send=st.form_submit_button("Send 📤",use_container_width=True)
        with c3: clr=st.form_submit_button("Clear 🗑️",use_container_width=True)
        if send and umsg:
            st.session_state.messages.append({"role":"user","content":umsg})
            with st.spinner("🤖 AI responding..."):
                r=chat_response(st.session_state.messages[:-1],umsg,loc)
            st.session_state.messages.append({"role":"assistant","content":r})
            # Also auto-run severity if emergency keywords detected
            if detect_crash_keywords(umsg) and not st.session_state.sev:
                with st.spinner("🤖 Emergency detected — auto-running full AI..."):
                    run_full_ai(umsg, coords, loc)
            st.rerun()
        if clr:
            st.session_state.messages=[]
            st.rerun()

# ══════════════════════════════════════════════
# TAB 6 — ANALYTICS
# ══════════════════════════════════════════════
with tab6:
    st.markdown("### 📊 Incident Analytics")
    analytics=get_analytics()
    for col,num,lbl in zip(st.columns(3),
        [str(analytics["total"]),
         str(next((c for s,c in analytics["by_severity"] if s=="CRITICAL"),0)),
         str(len(analytics["by_country"]))],
        ["Total Incidents","Critical Cases","Countries Active"]):
        with col:
            st.markdown(f'<div class="stat"><span class="n">{num}</span><span class="l">{lbl}</span></div>',
                unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    la,ra=st.columns(2)
    with la:
        st.markdown("#### 🌏 By Country")
        if analytics["by_country"]:
            for cn,count in analytics["by_country"]:
                pct=int((count/max(analytics["total"],1))*100)
                st.markdown(f"""<div style="margin:0.35rem 0">
                <div style="display:flex;justify-content:space-between;margin-bottom:3px">
                <span>{COUNTRY_FLAGS.get(cn,'🌏')} {cn}</span><span><b>{count}</b></span></div>
                <div style="background:#f0f0f0;border-radius:10px;height:7px">
                <div style="background:#e74c3c;width:{pct}%;height:7px;border-radius:10px"></div></div>
                </div>""", unsafe_allow_html=True)
        else: st.info("No incidents yet.")
    with ra:
        st.markdown("#### ⚠️ By Severity")
        sev_dict=dict(analytics["by_severity"])
        for s in ["CRITICAL","HIGH","MODERATE","LOW"]:
            count=sev_dict.get(s,0)
            color=get_severity_color(s)
            pct=int((count/max(analytics["total"],1))*100)
            st.markdown(f"""<div style="margin:0.35rem 0">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px">
            <span>{SEVERITY_EMOJIS.get(s,'')} {s}</span><span><b>{count}</b></span></div>
            <div style="background:#f0f0f0;border-radius:10px;height:7px">
            <div style="background:{color};width:{pct}%;height:7px;border-radius:10px"></div></div>
            </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#888;font-size:0.77rem;padding:0.8rem 0'>
🚨 <b>RoadSoS v3.0</b> — Night Wolfpack · Road Safety Hackathon 2026 · CoERS, IIT Madras · BIMSTEC<br>
<span style='color:#e74c3c'>In a life-threatening emergency, always call local emergency services first.</span>
</div>
""", unsafe_allow_html=True)
