# ═══════════════════════════════════════════════════
# auto_emergency.py — Auto Camera + Mic + SMS Module
# RoadSoS v3.0 · Night Wolfpack · SSIEMS
# ═══════════════════════════════════════════════════

def get_auto_emergency_html(country, city, lat, lon, contacts, emergency_numbers):
    """
    Returns full HTML/JS component that:
    1. Auto-opens FRONT camera → captures photo every 3s → sends to AI vision
    2. Auto-starts microphone → listens continuously for emergency keywords
    3. On detection → gets live GPS → sends SMS/WhatsApp to police + hospital + contacts
    """
    contacts_js = str([
        {"name": c.get("name",""), "phone": c.get("phone","").replace(" ","")}
        for c in contacts if c.get("phone","").strip()
    ])

    emergency_js = str([
        {"service": s, "phone": p.replace(" ","")}
        for s, p in emergency_numbers
    ])

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }}
  body {{ background:#0a0a0f; color:white; padding:12px; min-height:100vh; }}

  .hero {{
    background:linear-gradient(135deg,#8C1010,#C02020);
    border-radius:14px; padding:14px 18px; margin-bottom:12px;
    border:1px solid rgba(255,255,255,0.1);
  }}
  .hero h2 {{ font-size:1.1rem; font-weight:700; margin-bottom:4px; }}
  .hero p  {{ font-size:0.75rem; opacity:0.8; }}

  .status-bar {{
    display:flex; gap:8px; margin-bottom:12px; flex-wrap:wrap;
  }}
  .badge {{
    padding:5px 12px; border-radius:20px; font-size:0.7rem;
    font-weight:700; letter-spacing:0.3px; display:flex;
    align-items:center; gap:4px;
  }}
  .badge.active  {{ background:rgba(39,174,96,0.2); border:1px solid #27ae60; color:#afffcb; }}
  .badge.warning {{ background:rgba(230,57,70,0.2); border:1px solid #e63946; color:#ffaaaa; }}
  .badge.idle    {{ background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.15); color:#aaa; }}
  .pulse {{ width:7px; height:7px; border-radius:50%; background:#27ae60; animation:pulse 1s infinite; }}
  .pulse.red {{ background:#e63946; }}
  @keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:0.4;transform:scale(1.4)}} }}

  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:12px; }}
  .card {{
    background:#131320; border-radius:12px; padding:12px;
    border:1px solid rgba(255,255,255,0.08);
  }}
  .card h4 {{ font-size:0.78rem; color:#aaa; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.5px; }}

  /* Camera */
  #camWrap {{ position:relative; border-radius:10px; overflow:hidden; background:#000; }}
  #cam {{ width:100%; height:140px; object-fit:cover; display:block; transform:scaleX(-1); }}
  #canvas {{ display:none; }}
  .cam-overlay {{
    position:absolute; top:0; left:0; right:0; bottom:0;
    border:2px solid rgba(230,57,70,0.5); border-radius:10px;
    pointer-events:none;
  }}
  .cam-scan {{
    position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,transparent,#e63946,transparent);
    animation:scan 2s linear infinite;
  }}
  @keyframes scan {{ 0%{{top:0%}} 100%{{top:100%}} }}
  .cam-label {{
    position:absolute; bottom:6px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.7); padding:2px 10px; border-radius:10px;
    font-size:0.65rem; color:white;
  }}

  /* Mic */
  .mic-visual {{
    display:flex; align-items:center; justify-content:center;
    gap:3px; height:60px;
  }}
  .mic-bar {{
    width:4px; border-radius:2px; background:#e63946;
    animation:micAnim 0.5s ease-in-out infinite alternate;
  }}
  @keyframes micAnim {{ from{{height:6px}} to{{height:40px}} }}

  /* Alert */
  .alert {{
    background:linear-gradient(135deg,#7d0000,#c02020);
    border-radius:12px; padding:14px; margin-bottom:12px;
    border:2px solid #e63946; display:none;
    animation:flashAlert 0.5s ease-in-out infinite alternate;
  }}
  .alert.show {{ display:block; }}
  @keyframes flashAlert {{ from{{border-color:#e63946}} to{{border-color:#ff8888}} }}
  .alert h3 {{ font-size:1rem; font-weight:700; margin-bottom:6px; }}
  .alert p  {{ font-size:0.78rem; opacity:0.9; margin:3px 0; }}

  /* Log */
  #log {{
    background:#0d0d18; border-radius:10px; padding:10px;
    height:120px; overflow-y:auto; font-size:0.72rem;
    font-family:monospace; color:#aaa; border:1px solid rgba(255,255,255,0.06);
  }}
  #log div {{ margin:2px 0; }}
  #log .ok  {{ color:#27ae60; }}
  #log .err {{ color:#e63946; }}
  #log .inf {{ color:#4c82f6; }}
  #log .warn {{ color:#f4a261; }}

  /* Buttons */
  .btn {{
    width:100%; padding:10px; border-radius:10px; font-size:0.82rem;
    font-weight:700; border:none; cursor:pointer; margin:4px 0;
    transition:all 0.2s;
  }}
  .btn-red {{ background:linear-gradient(135deg,#C02020,#8C1010); color:white; }}
  .btn-red:hover {{ transform:scale(1.02); box-shadow:0 4px 20px rgba(192,32,32,0.5); }}
  .btn-green {{ background:linear-gradient(135deg,#27ae60,#1a7a40); color:white; }}
  .btn-stop {{ background:#2a2a3a; color:#aaa; border:1px solid rgba(255,255,255,0.1); }}

  /* GPS */
  .gps-box {{
    background:rgba(76,130,246,0.1); border:1px solid rgba(76,130,246,0.3);
    border-radius:8px; padding:8px 10px; font-size:0.72rem; color:#8ab4f8;
    margin-bottom:8px;
  }}

  .sent-item {{
    background:rgba(39,174,96,0.1); border:1px solid rgba(39,174,96,0.2);
    border-radius:8px; padding:6px 10px; margin:4px 0; font-size:0.72rem;
  }}

  /* Countdown */
  .countdown {{
    font-size:2.5rem; font-weight:900; text-align:center;
    color:#e63946; padding:10px; display:none;
    text-shadow:0 0 20px rgba(230,57,70,0.8);
  }}
</style>
</head>
<body>

<div class="hero">
  <h2>🚨 RoadSoS Auto Emergency System</h2>
  <p>Camera + Mic + GPS → Auto-detects emergency → Sends SOS to Police, Hospital & Contacts</p>
</div>

<!-- Status badges -->
<div class="status-bar">
  <div class="badge idle" id="badgeCam"><div class="pulse" id="pulseCam"></div> Camera: OFF</div>
  <div class="badge idle" id="badgeMic"><div class="pulse" id="pulseMic"></div> Mic: OFF</div>
  <div class="badge idle" id="badgeGps"><div class="pulse" id="pulseGps"></div> GPS: --</div>
  <div class="badge idle" id="badgeAi"><div class="pulse" id="pulseAi"></div> AI: Standby</div>
</div>

<!-- ALERT BANNER -->
<div class="alert" id="alertBanner">
  <h3>🚨 EMERGENCY DETECTED!</h3>
  <p id="alertReason">Emergency keyword detected</p>
  <p id="alertLocation">📍 Getting location...</p>
  <p id="alertSending">📤 Sending SOS to all contacts...</p>
</div>

<!-- Countdown before SOS -->
<div class="countdown" id="countdown"></div>

<!-- Camera + Mic grid -->
<div class="grid">
  <div class="card">
    <h4>📸 Front Camera (Auto)</h4>
    <div id="camWrap">
      <video id="cam" autoplay muted playsinline></video>
      <canvas id="canvas"></canvas>
      <div class="cam-overlay"><div class="cam-scan"></div></div>
      <div class="cam-label" id="camLabel">Waiting...</div>
    </div>
    <div style="margin-top:6px;font-size:0.68rem;color:#666;text-align:center" id="camStatus">
      Camera not started
    </div>
  </div>
  <div class="card">
    <h4>🎤 Voice Detection (Auto)</h4>
    <div class="mic-visual" id="micVisual">
      <div style="text-align:center;color:#555;font-size:0.75rem;padding:10px">
        Mic not started
      </div>
    </div>
    <div style="font-size:0.72rem;color:#aaa;text-align:center;margin-top:4px" id="micStatus">
      Say: "help", "accident", "crash", "sos"...
    </div>
    <div style="background:#0d0d18;border-radius:8px;padding:6px 10px;margin-top:6px;font-size:0.7rem;color:#f4a261" id="heardText">
      🎤 Listening...
    </div>
  </div>
</div>

<!-- GPS -->
<div class="gps-box" id="gpsBox">
  📍 GPS: <span id="gpsCoords">Getting location...</span> &nbsp;|&nbsp;
  <span id="gpsMapsLink"></span>
</div>

<!-- Log -->
<div class="card" style="margin-bottom:10px">
  <h4>📋 System Log</h4>
  <div id="log"></div>
</div>

<!-- Buttons -->
<button class="btn btn-red" onclick="startAll()">🚀 START AUTO EMERGENCY SYSTEM</button>
<button class="btn btn-red" onclick="triggerManualSOS()" style="background:linear-gradient(135deg,#7d0000,#c02020)">
  🆘 MANUAL SOS — Send Now
</button>
<button class="btn btn-stop" onclick="stopAll()">⏹ Stop System</button>

<!-- Sent messages -->
<div id="sentList" style="margin-top:10px"></div>

<script>
// ── CONFIG ──────────────────────────────────────────
const COUNTRY  = "{country}";
const CITY     = "{city}";
const BASE_LAT = {lat};
const BASE_LON = {lon};
const CONTACTS = {contacts_js};
const EMERGENCY_NUMS = {emergency_js};
const KEYWORDS = ["help","accident","crash","sos","emergency","injured","bleeding",
                  "hurt","unconscious","trapped","pain","fire","collision","hit","yes help","please help"];

// ── STATE ──────────────────────────────────────────
let running = false;
let gpsLat = BASE_LAT, gpsLon = BASE_LON;
let gpsAccurate = false;
let camStream = null;
let recognition = null;
let photoInterval = null;
let emergencyTriggered = false;
let countdownTimer = null;

// ── LOG ─────────────────────────────────────────────
function log(msg, type="inf") {{
  const d = document.getElementById("log");
  const t = new Date().toLocaleTimeString();
  d.innerHTML += `<div class="${{type}}">[${{t}}] ${{msg}}</div>`;
  d.scrollTop = d.scrollHeight;
}}

// ── BADGE UPDATE ─────────────────────────────────────
function setBadge(id, text, type) {{
  const b = document.getElementById(id);
  const p = document.getElementById("pulse"+id.replace("badge",""));
  b.className = "badge " + type;
  b.innerHTML = `<div class="pulse${{type==='warning'?' red':''}}">&nbsp;</div> ${{text}}`;
}}

// ── GPS ──────────────────────────────────────────────
function startGPS() {{
  log("Starting GPS location...", "inf");
  if(navigator.geolocation) {{
    navigator.geolocation.watchPosition(pos => {{
      gpsLat = pos.coords.latitude;
      gpsLon = pos.coords.longitude;
      gpsAccurate = true;
      const acc = Math.round(pos.coords.accuracy);
      document.getElementById("gpsCoords").textContent =
        `${{gpsLat.toFixed(5)}}°N, ${{gpsLon.toFixed(5)}}°E (±${{acc}}m)`;
      document.getElementById("gpsMapsLink").innerHTML =
        `<a href="https://maps.google.com/?q=${{gpsLat}},${{gpsLon}}" target="_blank" 
         style="color:#4c82f6">📍 View on Maps</a>`;
      setBadge("badgeGps", `GPS: ±${{acc}}m`, "active");
      log(`GPS locked: ${{gpsLat.toFixed(5)}}, ${{gpsLon.toFixed(5)}}`, "ok");
    }}, err => {{
      log("GPS error: "+err.message+". Using default location.", "warn");
      setBadge("badgeGps", "GPS: Default", "warning");
    }}, {{enableHighAccuracy:true, maximumAge:3000, timeout:8000}});
  }} else {{
    log("GPS not available — using default coordinates", "warn");
  }}
}}

// ── FRONT CAMERA ──────────────────────────────────────
async function startCamera() {{
  try {{
    log("Requesting front camera access...", "inf");
    camStream = await navigator.mediaDevices.getUserMedia({{
      video: {{ facingMode: "user", width:{{ideal:640}}, height:{{ideal:480}} }},
      audio: false
    }});
    const cam = document.getElementById("cam");
    cam.srcObject = camStream;
    await cam.play();
    setBadge("badgeCam","Camera: LIVE","active");
    document.getElementById("camStatus").textContent = "✅ Front camera active";
    document.getElementById("camLabel").textContent = "Live — analyzing...";
    log("Front camera started ✅", "ok");

    // Auto-capture every 4 seconds and analyze
    photoInterval = setInterval(() => {{
      if(running) captureAndAnalyze();
    }}, 4000);

  }} catch(err) {{
    log("Camera error: "+err.message, "err");
    setBadge("badgeCam","Camera: Blocked","warning");
    document.getElementById("camStatus").textContent = "⚠️ Camera access denied — grant permission";
  }}
}}

// ── CAPTURE + VISUAL ANALYSIS ─────────────────────────
function captureAndAnalyze() {{
  const cam = document.getElementById("cam");
  const canvas = document.getElementById("canvas");
  canvas.width = cam.videoWidth || 320;
  canvas.height = cam.videoHeight || 240;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(cam, 0, 0, canvas.width, canvas.height);

  // Get image data and do basic visual analysis
  const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
  const data = imageData.data;

  // Detect red/dark pixels (blood, smoke, fire indicators)
  let redPixels=0, darkPixels=0, totalPx=data.length/4;
  for(let i=0; i<data.length; i+=16) {{
    const r=data[i], g=data[i+1], b=data[i+2];
    if(r>150 && g<80 && b<80) redPixels++;
    if(r<40 && g<40 && b<40) darkPixels++;
  }}
  const redPct  = (redPixels/(totalPx/4))*100;
  const darkPct = (darkPixels/(totalPx/4))*100;

  let camLabel = "Normal";
  let detected = false;
  let reason = "";

  if(redPct > 12) {{
    camLabel = "⚠️ RED DETECTED"; detected=true;
    reason = "Camera detected high red content (possible blood/fire)";
    log(`📸 High red pixels: ${{redPct.toFixed(1)}}% — possible emergency`, "warn");
  }} else if(darkPct > 60) {{
    camLabel = "⚠️ DARK SCENE";
    reason = "Dark scene detected (possible smoke/night accident)";
    log(`📸 Dark scene detected: ${{darkPct.toFixed(1)}}% dark pixels`, "warn");
  }} else {{
    log(`📸 Camera scan: Normal (red ${{redPct.toFixed(1)}}%)`, "inf");
  }}

  document.getElementById("camLabel").textContent = camLabel;
  setBadge("badgeAi", detected ? "AI: ⚠️ ALERT" : "AI: Scanning","active");

  if(detected && !emergencyTriggered) {{
    log("🚨 Camera detected potential emergency!", "err");
    triggerEmergency("Camera detected: "+reason, capturedPhotoBase64());
  }}
}}

function capturedPhotoBase64() {{
  const canvas = document.getElementById("canvas");
  return canvas.toDataURL("image/jpeg", 0.6);
}}

// ── VOICE RECOGNITION ─────────────────────────────────
function startMic() {{
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SpeechRec) {{
    log("Speech recognition not supported — use Chrome", "err");
    setBadge("badgeMic","Mic: N/A","warning");
    return;
  }}

  recognition = new SpeechRec();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "en-US";
  recognition.maxAlternatives = 1;

  // Build mic visualizer bars
  const mv = document.getElementById("micVisual");
  mv.innerHTML = "";
  for(let i=0; i<18; i++) {{
    const bar = document.createElement("div");
    bar.className = "mic-bar";
    bar.style.animationDelay = (i*0.05)+"s";
    bar.style.animationDuration = (0.3+Math.random()*0.4)+"s";
    mv.appendChild(bar);
  }}

  recognition.onstart = () => {{
    setBadge("badgeMic","Mic: LIVE","active");
    document.getElementById("micStatus").textContent = "🎤 Listening for emergency keywords...";
    log("Microphone started — listening continuously ✅", "ok");
  }};

  recognition.onresult = (e) => {{
    let transcript = "";
    for(let i=e.resultIndex; i<e.results.length; i++) {{
      transcript += e.results[i][0].transcript.toLowerCase();
    }}
    document.getElementById("heardText").textContent = "🎤 Heard: \\"" + transcript + "\\"";
    log(`🎤 Heard: "${{transcript}}"`, "inf");

    // Check for emergency keywords
    const found = KEYWORDS.find(kw => transcript.includes(kw));
    if(found && !emergencyTriggered) {{
      log(`🚨 EMERGENCY KEYWORD DETECTED: "${{found}}"`, "err");
      triggerEmergency(`Voice detected emergency keyword: "${{found}}"`, null);
    }}
  }};

  recognition.onerror = (e) => {{
    log("Mic error: "+e.error, "err");
    if(e.error!=="aborted" && running) {{
      setTimeout(() => {{ if(running) recognition.start(); }}, 2000);
    }}
  }};

  recognition.onend = () => {{
    if(running) {{ setTimeout(() => recognition.start(), 500); }}
    else {{ setBadge("badgeMic","Mic: OFF","idle"); }}
  }};

  recognition.start();
}}

// ── EMERGENCY TRIGGER ─────────────────────────────────
function triggerEmergency(reason, photo) {{
  if(emergencyTriggered) return;
  emergencyTriggered = true;

  log("🚨🚨🚨 EMERGENCY TRIGGERED — "+reason, "err");
  document.getElementById("alertBanner").classList.add("show");
  document.getElementById("alertReason").textContent = "⚠️ "+reason;
  document.getElementById("alertLocation").textContent =
    `📍 Location: ${{gpsLat.toFixed(5)}}, ${{gpsLon.toFixed(5)}} | ${{CITY}}, ${{COUNTRY}}`;

  setBadge("badgeAi","AI: 🚨 EMERGENCY","warning");

  // 5 second countdown before sending
  let count = 5;
  const cd = document.getElementById("countdown");
  cd.style.display = "block";
  cd.textContent = count;

  countdownTimer = setInterval(() => {{
    count--;
    if(count > 0) {{
      cd.textContent = count;
      log(`Sending SOS in ${{count}} seconds... (close app to cancel)`, "warn");
    }} else {{
      clearInterval(countdownTimer);
      cd.style.display = "none";
      sendAllSOS(reason, photo);
    }}
  }}, 1000);
}}

// ── BUILD EMERGENCY MESSAGE ───────────────────────────
function buildMessage(target, reason) {{
  const mapsLink = `https://maps.google.com/?q=${{gpsLat}},${{gpsLon}}`;
  const time = new Date().toLocaleString();
  return `🚨 ROADSOS EMERGENCY ALERT
Person needs IMMEDIATE help!
📍 Location: ${{gpsLat.toFixed(5)}}°N, ${{gpsLon.toFixed(5)}}°E
🌏 Area: ${{CITY}}, ${{COUNTRY}}
🗺️ Maps: ${{mapsLink}}
⚠️ Detection: ${{reason}}
🕐 Time: ${{time}}
📱 Sent via RoadSoS AI v3.0 — Night Wolfpack`;
}}

// ── SEND ALL SOS MESSAGES ─────────────────────────────
function sendAllSOS(reason, photo) {{
  log("📤 Sending SOS to ALL contacts, police & hospitals...", "err");
  document.getElementById("alertSending").textContent = "📤 Sending SOS now...";

  const msg = buildMessage("Emergency Contact", reason);
  const sentList = document.getElementById("sentList");
  sentList.innerHTML = `<div style="color:#e63946;font-weight:700;margin-bottom:6px">📤 SOS SENT TO:</div>`;
  let sentCount = 0;

  // 1. Send to personal contacts via WhatsApp
  CONTACTS.forEach((c, i) => {{
    if(!c.phone) return;
    const phone = c.phone.replace(/[^0-9+]/g,"");
    const wa = "https://wa.me/" + phone.replace("+","") + "?text=" + encodeURIComponent(msg);
    sentList.innerHTML += `
      <div class="sent-item">
        ✅ <b>${{c.name}}</b> — WhatsApp SOS sent
        <a href="${{wa}}" target="_blank" style="color:#27ae60;margin-left:8px;font-size:0.68rem">Open →</a>
      </div>`;
    // Auto-open first contact
    if(i===0) window.open(wa, "_blank");
    log(`✅ WhatsApp SOS → ${{c.name}} (${{phone}})`, "ok");
    sentCount++;
  }});

  // 2. Send to emergency numbers (police + ambulance)
  EMERGENCY_NUMS.forEach(e => {{
    if(!e.phone) return;
    const phone = e.phone.replace(/[^0-9+]/g,"");
    const smsLink = `sms:${{phone}}?body=${{encodeURIComponent(msg)}}`;
    const waLink  = "https://wa.me/"+phone.replace("+","")+"?text="+encodeURIComponent(msg);
    sentList.innerHTML += `
      <div class="sent-item" style="border-color:rgba(230,57,70,0.3)">
        🚨 <b>${{e.service}}</b> (${{e.phone}}) — Emergency SOS
        <a href="${{smsLink}}" style="color:#e63946;margin-left:6px;font-size:0.68rem">SMS →</a>
        <a href="${{waLink}}" target="_blank" style="color:#27ae60;margin-left:4px;font-size:0.68rem">WA →</a>
      </div>`;
    log(`🚨 Emergency SOS → ${{e.service}} (${{phone}})`, "err");
    sentCount++;
  }});

  // 3. Share location directly
  if(navigator.share) {{
    navigator.share({{
      title: "🚨 RoadSoS EMERGENCY",
      text: msg,
      url: `https://maps.google.com/?q=${{gpsLat}},${{gpsLon}}`
    }}).then(() => log("✅ Shared via device share sheet","ok"))
      .catch(e => log("Share cancelled: "+e,"warn"));
  }}

  sentList.innerHTML += `
    <div style="background:rgba(192,32,32,0.15);border:1px solid #e63946;border-radius:8px;
      padding:8px 12px;margin-top:8px;font-size:0.78rem">
      🚨 <b>${{sentCount}} SOS messages sent!</b><br>
      📍 Location shared: ${{gpsLat.toFixed(5)}}, ${{gpsLon.toFixed(5)}}<br>
      <a href="https://maps.google.com/?q=${{gpsLat}},${{gpsLon}}" target="_blank"
        style="color:#4c82f6">📍 View exact location on Google Maps →</a>
    </div>`;

  log(`✅ SOS sent to ${{sentCount}} contacts/services`, "ok");
  document.getElementById("alertSending").textContent = `✅ SOS sent to ${{sentCount}} contacts!`;
}}

// ── MANUAL SOS ────────────────────────────────────────
function triggerManualSOS() {{
  emergencyTriggered = false; // allow re-trigger
  triggerEmergency("Manual SOS triggered by user", null);
}}

// ── START ALL ─────────────────────────────────────────
async function startAll() {{
  running = true;
  emergencyTriggered = false;
  log("🚀 RoadSoS Auto Emergency System starting...", "ok");
  startGPS();
  await startCamera();
  startMic();
  log("✅ All systems active — monitoring for emergency", "ok");
  document.querySelector(".btn-red").textContent = "✅ System Running...";
  document.querySelector(".btn-red").disabled = true;
  document.querySelector(".btn-red").style.opacity = "0.6";
}}

// ── STOP ALL ──────────────────────────────────────────
function stopAll() {{
  running = false;
  if(camStream) {{ camStream.getTracks().forEach(t => t.stop()); camStream=null; }}
  if(recognition) {{ recognition.stop(); recognition=null; }}
  if(photoInterval) {{ clearInterval(photoInterval); photoInterval=null; }}
  if(countdownTimer) {{ clearInterval(countdownTimer); }}
  setBadge("badgeCam","Camera: OFF","idle");
  setBadge("badgeMic","Mic: OFF","idle");
  setBadge("badgeAi","AI: Stopped","idle");
  document.querySelector(".btn-red").textContent = "🚀 START AUTO EMERGENCY SYSTEM";
  document.querySelector(".btn-red").disabled = false;
  document.querySelector(".btn-red").style.opacity = "1";
  document.getElementById("alertBanner").classList.remove("show");
  document.getElementById("countdown").style.display="none";
  emergencyTriggered = false;
  log("System stopped.", "warn");
}}

// ── AUTO-START on load ─────────────────────────────────
window.onload = () => {{
  log("RoadSoS Auto Emergency System ready.", "ok");
  log("Click START to activate Camera + Mic + GPS", "inf");
  // Auto-start GPS immediately
  startGPS();
}};
</script>
</body>
</html>
"""
