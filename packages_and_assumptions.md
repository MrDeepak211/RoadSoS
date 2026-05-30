# RoadSoS v3.0 — Software Packages & Assumptions

## Software Packages Used

| Package | Version | Purpose |
|---|---|---|
| streamlit | >=1.32.0 | Web UI framework |
| requests | >=2.31.0 | Anthropic Claude API calls |
| geopy | >=2.4.1 | Geocoding utilities |
| folium | >=0.15.0 | Interactive map rendering |
| streamlit-folium | >=0.18.0 | Folium maps inside Streamlit |
| sqlite3 | Python stdlib | Offline local database |
| math | Python stdlib | Haversine distance calculation |
| json | Python stdlib | Data serialization |
| os | Python stdlib | Environment variable access |
| urllib.parse | Python stdlib | URL encoding for SMS/WhatsApp links |

## External APIs Used
| API | Type | Cost |
|---|---|---|
| Anthropic Claude API | AI chatbot, severity detection, translation, first aid | Free tier available |
| Twilio SMS API | SMS alerts (optional) | Free trial (15 credits) |
| Web Speech API | Browser-native voice recognition | Free (browser built-in) |
| OpenStreetMap | Map tiles via Folium | Free / open source |
| Google Maps (deep link) | Navigation redirect only | Free |

> Open models and free APIs preferred as per Section 8.2 of rulebook.

## Architecture
```
RoadSoS_v3/
├── app.py                    # Main Streamlit application (6 tabs)
├── requirements.txt
├── packages_and_assumptions.md
├── modules/
│   ├── __init__.py
│   ├── database.py           # SQLite DB + all BIMSTEC emergency data
│   ├── ai_assistant.py       # Claude API integration + all AI features
│   ├── utils.py              # Constants, helpers, configs
│   ├── voice_sos.py          # Web Speech API component (HTML/JS)
│   ├── live_map.py           # Folium map builder + GPS HTML component
│   └── sms_alert.py          # Twilio SMS + WhatsApp fallback
└── data/
    └── roadsos.db            # Auto-generated SQLite database
```

## New Features in v3.0
1. **Voice SOS** — Browser Web Speech API detects crash keywords, triggers protocol
2. **Live Map + GPS** — Folium OpenStreetMap with markers, routes, GPS detection
3. **SMS Alert System** — Twilio real SMS + WhatsApp deep link fallback

## Assumptions
1. GPS detection requires browser permission (HTTPS recommended)
2. Voice recognition works best in Chrome/Edge browsers
3. Twilio SMS is optional — WhatsApp/SMS links work as free fallback
4. ETA calculated at ~30 km/h emergency response speed (urban estimate)
5. Haversine formula gives straight-line distance; road distance may vary
6. SQLite for offline-first design
7. All hospital/police data sourced from public government health ministry records
