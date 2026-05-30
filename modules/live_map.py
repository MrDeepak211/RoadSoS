"""
Live Map Module
Uses Folium for interactive maps with emergency service markers,
GPS location, and route visualization.
"""
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


SERVICE_COLORS = {
    "hospital": "red",
    "ambulance": "orange",
    "police": "blue",
    "rescue": "green"
}

SERVICE_ICONS = {
    "hospital": "plus-sign",
    "ambulance": "ambulance",
    "police": "star",
    "rescue": "fire-station"
}

def build_emergency_map(user_lat, user_lon, nearby_services, severity=None, zoom=13):
    """Build a Folium map with user location and nearby services"""
    try:
        import folium
        from folium import plugins

        # Determine map center
        m = folium.Map(
            location=[user_lat, user_lon],
            zoom_start=zoom,
            tiles="OpenStreetMap"
        )

        # Severity color for user marker
        sev_colors = {
            "CRITICAL": "red", "HIGH": "orange",
            "MODERATE": "lightred", "LOW": "green"
        }
        user_color = sev_colors.get(severity, "red") if severity else "red"

        # User location marker (pulsing)
        folium.Marker(
            location=[user_lat, user_lon],
            popup=folium.Popup("<b>🚨 YOUR LOCATION</b><br>Accident Site", max_width=200),
            tooltip="📍 You are here",
            icon=folium.Icon(color=user_color, icon="exclamation-sign", prefix="glyphicon")
        ).add_to(m)

        # Pulsing circle around user
        folium.Circle(
            location=[user_lat, user_lon],
            radius=300,
            color="#e74c3c",
            fill=True,
            fill_color="#e74c3c",
            fill_opacity=0.15,
            weight=2
        ).add_to(m)

        # Add search radius circle (5km)
        folium.Circle(
            location=[user_lat, user_lon],
            radius=5000,
            color="#3498db",
            fill=False,
            weight=1,
            dash_array="5",
            tooltip="5km search radius"
        ).add_to(m)

        # Add emergency service markers
        for svc in nearby_services:
            color = SERVICE_COLORS.get(svc["type"], "gray")
            dist = svc["distance_km"]
            eta = svc.get("eta_minutes", "?")
            trauma_badge = "⭐ Level 1 Trauma" if svc.get("trauma_level") == 1 else ""

            popup_html = f"""
            <div style="font-family:sans-serif;min-width:180px">
                <b style="color:#c0392b">{svc['name']}</b><br>
                <small>{svc.get('city','')}, {svc.get('country','')}</small><br>
                <hr style="margin:4px 0">
                📞 <b>{svc['phone']}</b><br>
                📍 {svc.get('address','')}<br>
                🚗 {dist} km away · ~{eta} min ETA<br>
                {trauma_badge}
            </div>
            """

            folium.Marker(
                location=[svc["lat"], svc["lon"]],
                popup=folium.Popup(popup_html, max_width=220),
                tooltip=f"{svc['name']} ({dist}km)",
                icon=folium.Icon(
                    color=color,
                    icon="plus-sign" if svc["type"] == "hospital" else "info-sign",
                    prefix="glyphicon"
                )
            ).add_to(m)

            # Draw line from user to nearest (first) service
            if nearby_services and svc == nearby_services[0]:
                folium.PolyLine(
                    locations=[[user_lat, user_lon], [svc["lat"], svc["lon"]]],
                    color="#e74c3c",
                    weight=3,
                    opacity=0.8,
                    dash_array="8",
                    tooltip=f"Route to {svc['name']}"
                ).add_to(m)

        # Add fullscreen control
        try:
            plugins.Fullscreen().add_to(m)
        except:
            pass

        # Legend
        legend_html = """
        <div style="position:fixed; bottom:20px; left:20px; z-index:9999;
            background:white; padding:10px 14px; border-radius:10px;
            box-shadow:0 2px 10px rgba(0,0,0,0.2); font-size:12px; font-family:sans-serif;">
            <b>Legend</b><br>
            🔴 Accident Site<br>
            🔴 Hospital / Trauma<br>
            🟠 Ambulance<br>
            🔵 Police Station<br>
            🟢 Rescue Service
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))

        return m

    except ImportError:
        return None


def get_gps_html():
    """HTML component for GPS auto-detection"""
    return """
    <div id="gps-container" style="
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 14px; padding: 1.2rem;
        color: white; font-family: sans-serif;
        border: 1px solid rgba(52,152,219,0.3);
    ">
        <h4 style="margin:0 0 0.5rem 0; font-size:1rem;">📡 GPS Auto-Detection</h4>
        <p id="gps-status" style="margin:0 0 0.8rem 0; opacity:0.7; font-size:0.83rem;">
            Click to detect your exact location automatically
        </p>
        <button onclick="getLocation()" id="gps-btn" style="
            background: linear-gradient(135deg, #2980b9, #3498db);
            color:white; border:none; border-radius:50px;
            padding:0.6rem 1.5rem; cursor:pointer; width:100%;
            font-size:0.9rem; font-weight:600;
        ">📡 Detect My Location</button>
        <div id="coords-display" style="display:none; margin-top:0.8rem;
            background:rgba(255,255,255,0.05); border-radius:8px; padding:0.6rem;">
            <div id="coords-text" style="font-size:0.85rem;"></div>
        </div>
    </div>

    <script>
    function getLocation() {
        const btn = document.getElementById('gps-btn');
        const status = document.getElementById('gps-status');
        btn.textContent = '🔄 Detecting...';
        btn.disabled = true;
        status.textContent = 'Getting your GPS coordinates...';

        if (!navigator.geolocation) {
            status.textContent = '⚠️ GPS not supported. Select location manually.';
            btn.textContent = '📡 Detect My Location';
            btn.disabled = false;
            return;
        }

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const lat = pos.coords.latitude.toFixed(5);
                const lon = pos.coords.longitude.toFixed(5);
                const acc = pos.coords.accuracy.toFixed(0);
                status.textContent = '✅ Location detected!';
                btn.textContent = '✅ Location Found';
                document.getElementById('coords-display').style.display = 'block';
                document.getElementById('coords-text').innerHTML =
                    `📍 Lat: <b>${lat}</b> · Lon: <b>${lon}</b><br>🎯 Accuracy: ±${acc}m`;
                // Send to Streamlit
                window.parent.postMessage({
                    type: 'GPS_LOCATION',
                    lat: parseFloat(lat),
                    lon: parseFloat(lon),
                    accuracy: parseFloat(acc)
                }, '*');
            },
            (err) => {
                status.textContent = '⚠️ ' + (err.code === 1 ? 'Permission denied. Enable location access.' : 'Could not get location.');
                btn.textContent = '📡 Try Again';
                btn.disabled = false;
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    }
    </script>
    """
