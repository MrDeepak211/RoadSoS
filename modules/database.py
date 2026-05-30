import sqlite3
import math
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "roadsos.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS emergency_services (
        id INTEGER PRIMARY KEY,
        country TEXT, city TEXT, name TEXT, service_type TEXT,
        phone TEXT, latitude REAL, longitude REAL, address TEXT,
        available_24h INTEGER DEFAULT 1, trauma_level INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS emergency_numbers (
        id INTEGER PRIMARY KEY, country TEXT, service TEXT, number TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS incident_logs (
        id INTEGER PRIMARY KEY,
        timestamp TEXT, country TEXT, city TEXT,
        severity TEXT, incident_type TEXT, services_contacted TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY,
        date TEXT, country TEXT, city TEXT,
        incident_count INTEGER DEFAULT 0
    )''')

    SERVICES = [
        # INDIA
        # BANGLADESH
        ("Bangladesh","Dhaka","Dhaka Medical College Hospital","hospital","+880-2-55165088",23.7232,90.3914,"Secretariat Rd",1,1),
        ("Bangladesh","Dhaka","National Institute of Traumatology","hospital","+880-2-9128564",23.7268,90.3854,"Sher-E-Bangla Nagar",1,1),
        ("Bangladesh","Dhaka","Dhaka Metropolitan Police","police","999",23.7104,90.4074,"DMP HQ Minto Road",1,1),
        ("Bangladesh","Dhaka","National Ambulance Service","ambulance","999",23.7104,90.4074,"Central Dispatch",1,1),
        ("Bangladesh","Chittagong","Chittagong Medical College","hospital","+880-31-630954",22.3569,91.7832,"K B Fazlul Kader Rd",1,1),
        # SRI LANKA
        ("Sri Lanka","Colombo","National Hospital Colombo","hospital","+94-11-2691111",6.9271,79.8612,"Regent Street Colombo 8",1,1),
        ("Sri Lanka","Colombo","Colombo South Teaching Hospital","hospital","+94-11-2513072",6.8770,79.8600,"Kalubowila",1,1),
        ("Sri Lanka","Colombo","Sri Lanka Police HQ","police","119",6.9271,79.8612,"Headquarters Colombo",1,1),
        ("Sri Lanka","Colombo","1990 Suwa Seriya Ambulance","ambulance","1990",6.9271,79.8612,"National Dispatch",1,1),
        # NEPAL
        ("Nepal","Kathmandu","TUTH Trauma Centre","hospital","+977-1-4412404",27.7348,85.3320,"Maharajgunj",1,1),
        ("Nepal","Kathmandu","Bir Hospital","hospital","+977-1-4221119",27.7041,85.3131,"Kanti Path",1,1),
        ("Nepal","Kathmandu","Nepal Police HQ","police","100",27.7172,85.3240,"Naxal Kathmandu",1,1),
        ("Nepal","Kathmandu","Nepal Ambulance Service","ambulance","102",27.7172,85.3240,"Central Dispatch",1,1),
        # MYANMAR
        ("Myanmar","Yangon","Yangon General Hospital","hospital","+95-1-256112",16.8207,96.1735,"Bogyoke Aung San Rd",1,1),
        ("Myanmar","Yangon","Myanmar Police Force","police","199",16.8409,96.1735,"Police HQ Yangon",1,1),
        ("Myanmar","Yangon","Yangon Ambulance Service","ambulance","192",16.8409,96.1735,"Central Dispatch",1,1),
        # THAILAND
        ("Thailand","Bangkok","Ramathibodi Hospital Trauma","hospital","+66-2-201-1000",13.7649,100.5284,"270 Rama VI Rd",1,1),
        ("Thailand","Bangkok","Bumrungrad International Hospital","hospital","+66-2-066-8888",13.7420,100.5556,"33 Sukhumvit 3",1,2),
        ("Thailand","Bangkok","Tourist Police Bangkok","police","1155",13.7563,100.5018,"Unico House Lumphini",1,1),
        ("Thailand","Bangkok","Narenthorn EMS Center","ambulance","1669",13.7563,100.5018,"National EMS Center",1,1),
        # BHUTAN
        ("Bhutan","Thimphu","JDWNR Hospital Trauma Unit","hospital","+975-2-322496",27.4661,89.6419,"Gongphel Lam Thimphu",1,1),
        ("Bhutan","Thimphu","Royal Bhutan Police","police","113",27.4661,89.6419,"Police HQ Thimphu",1,1),
        ("Bhutan","Thimphu","Bhutan Ambulance","ambulance","112",27.4661,89.6419,"JDWNRH Dispatch",1,1),
    ]

    c.executemany("INSERT OR IGNORE INTO emergency_services VALUES (NULL,?,?,?,?,?,?,?,?,?,?)", SERVICES)

    EMERGENCY_NUMBERS = [
        ("Bangladesh","Police/Emergency","999"), ("Bangladesh","Fire","199"), ("Bangladesh","Coast Guard","243"),
        ("Sri Lanka","Police","119"), ("Sri Lanka","Ambulance","1990"), ("Sri Lanka","Fire","110"), ("Sri Lanka","Accident Service","1938"),
        ("Nepal","Police","100"), ("Nepal","Ambulance","102"), ("Nepal","Fire","101"), ("Nepal","Tourist Police","1144"),
        ("Myanmar","Police","199"), ("Myanmar","Ambulance","192"), ("Myanmar","Fire","191"),
        ("Thailand","Police","191"), ("Thailand","Ambulance/EMS","1669"), ("Thailand","Tourist Police","1155"), ("Thailand","Highway Police","1193"),
        ("Bhutan","Police","113"), ("Bhutan","Ambulance","112"), ("Bhutan","Fire","110"),
    ]

    c.executemany("INSERT OR IGNORE INTO emergency_numbers VALUES (NULL,?,?,?)", EMERGENCY_NUMBERS)
    conn.commit()
    conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def get_nearby_services(lat, lon, service_type=None, limit=6):
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM emergency_services"
    params = ()
    if service_type:
        query += " WHERE service_type=?"
        params = (service_type,)
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    results = []
    for row in rows:
        dist = haversine(lat, lon, row[6], row[7])
        eta_min = int(dist / 0.5)  # Estimated ETA: ~30km/h in emergency
        results.append({
            "id": row[0], "country": row[1], "city": row[2], "name": row[3],
            "type": row[4], "phone": row[5], "lat": row[6], "lon": row[7],
            "address": row[8], "distance_km": round(dist, 1),
            "eta_minutes": min(eta_min, 120), "trauma_level": row[10]
        })
    results.sort(key=lambda x: x["distance_km"])
    return results[:limit]

def get_nearest_trauma_center(lat, lon):
    services = get_nearby_services(lat, lon, service_type="hospital", limit=10)
    trauma = [s for s in services if s["trauma_level"] == 1]
    return trauma[0] if trauma else (services[0] if services else None)

def get_emergency_numbers(country):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT service, number FROM emergency_numbers WHERE country=?", (country,))
    rows = c.fetchall()
    conn.close()
    return rows

def log_incident(country, city, severity, incident_type, services):
    from datetime import datetime
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO incident_logs VALUES (NULL,?,?,?,?,?,?)",
        (datetime.now().isoformat(), country, city, severity, incident_type, services)
    )
    conn.commit()
    conn.close()

def get_analytics():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT country, COUNT(*) as cnt FROM incident_logs GROUP BY country ORDER BY cnt DESC")
    by_country = c.fetchall()
    c.execute("SELECT severity, COUNT(*) as cnt FROM incident_logs GROUP BY severity")
    by_severity = c.fetchall()
    c.execute("SELECT COUNT(*) FROM incident_logs")
    total = c.fetchone()[0]
    conn.close()
    return {"by_country": by_country, "by_severity": by_severity, "total": total}
