def get_voice_component_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    * { margin:0; padding:0; box-sizing:border-box; font-family:'Segoe UI',sans-serif; }
    body { background:transparent; }
    .container { padding:10px; }
    .status-bar {
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius:12px; padding:12px 16px; margin-bottom:10px;
        color:white; font-size:13px; border-left:4px solid #e74c3c;
        display:flex; align-items:center; gap:10px;
    }
    .pulse { width:10px; height:10px; border-radius:50%; background:#e74c3c;
        animation:pulse 1s infinite; flex-shrink:0; }
    @keyframes pulse { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.4);opacity:0.5} }
    .transcript-box {
        background:#0d1117; color:#e6edf3; border-radius:10px;
        padding:10px 14px; font-size:12px; min-height:40px;
        margin-bottom:8px; border:1px solid #30363d;
    }
    .alert-box {
        background:linear-gradient(135deg,#7b0000,#c0392b);
        color:white; border-radius:10px; padding:10px 14px;
        font-size:12px; display:none; margin-bottom:8px;
        animation:flash 0.5s ease-in-out 6;
    }
    @keyframes flash { 0%,100%{opacity:1} 50%{opacity:0.3} }
    </style>
    </head>
    <body>
    <div class="container">
        <div class="status-bar">
            <div class="pulse" id="dot"></div>
            <span id="statusTxt">🎤 Initializing voice detection...</span>
        </div>
        <div class="transcript-box" id="transcript">Listening for emergency keywords...</div>
        <div class="alert-box" id="alertBox">🚨 EMERGENCY DETECTED! Sending alerts...</div>
    </div>
    <script>
    const KEYWORDS = ["accident","crash","help","emergency","sos","bleeding","injured",
                      "unconscious","pain","fire","trapped","hurt","yes","ambulance","police"];
    let recognition = null;
    const dot = document.getElementById("dot");
    const statusTxt = document.getElementById("statusTxt");
    const transcript = document.getElementById("transcript");
    const alertBox = document.getElementById("alertBox");

    function startVoice() {
        if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
            statusTxt.textContent = "❌ Voice not supported in this browser";
            return;
        }
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SR();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-US";

        recognition.onstart = () => {
            dot.style.background = "#27ae60";
            statusTxt.textContent = "🎤 LIVE — Listening for emergency keywords...";
        };
        recognition.onresult = (e) => {
            let text = "";
            for (let i = e.resultIndex; i < e.results.length; i++) {
                text += e.results[i][0].transcript;
            }
            transcript.textContent = "🗣️ " + text;
            const lower = text.toLowerCase();
            if (KEYWORDS.some(k => lower.includes(k))) {
                dot.style.background = "#e74c3c";
                statusTxt.textContent = "🚨 EMERGENCY KEYWORD DETECTED!";
                alertBox.style.display = "block";
                alertBox.textContent = "🚨 EMERGENCY DETECTED: \"" + text + "\" — Sending alerts...";
                window.parent.postMessage({type:"EMERGENCY_DETECTED", text: text}, "*");
            }
        };
        recognition.onerror = () => { startVoice(); };
        recognition.onend = () => { startVoice(); };
        recognition.start();
    }
    startVoice();
    </script>
    </body>
    </html>
    """
