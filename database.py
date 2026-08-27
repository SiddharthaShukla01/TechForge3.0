import sqlite3
import pandas as pd
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "disaster.db"

# Complete Coordinate Map for all 13 Districts of Uttarakhand
DISTRICT_COORDINATES = {
    "Dehradun": (30.3165, 78.0322),
    "Haridwar": (29.9457, 78.1642),
    "Tehri Garhwal": (30.3800, 78.4800),
    "Chamoli": (30.5500, 79.5667),
    "Uttarkashi": (30.7268, 78.4354),
    "Rudraprayag": (30.2844, 78.9811),
    "Pauri Garhwal": (30.1500, 78.7800),
    "Pithoragarh": (29.5828, 80.2182),
    "Bageshwar": (29.8406, 79.7694),
    "Almora": (29.5971, 79.6591),
    "Champawat": (29.3347, 80.0911),
    "Nainital": (29.3919, 79.4542),
    "Udham Singh Nagar": (28.9800, 79.4000)
}

DISTRICT_NAMES_MAP = {
    "Dehradun": {"en": "Dehradun", "hi": "देहरादून (Dehradun)"},
    "Haridwar": {"en": "Haridwar", "hi": "हरिद्वार (Haridwar)"},
    "Tehri Garhwal": {"en": "Tehri Garhwal", "hi": "टिहरी गढ़वाल (Tehri Garhwal)"},
    "Chamoli": {"en": "Chamoli", "hi": "चमोली (Chamoli)"},
    "Uttarkashi": {"en": "Uttarkashi", "hi": "उत्तरकाशी (Uttarkashi)"},
    "Rudraprayag": {"en": "Rudraprayag", "hi": "रुद्रप्रयाग (Rudraprayag)"},
    "Pauri Garhwal": {"en": "Pauri Garhwal", "hi": "पौड़ी गढ़वाल (Pauri Garhwal)"},
    "Pithoragarh": {"en": "Pithoragarh", "hi": "पिथौरागढ़ (Pithoragarh)"},
    "Bageshwar": {"en": "Bageshwar", "hi": "बागेश्वर (Bageshwar)"},
    "Almora": {"en": "Almora", "hi": "अल्मोड़ा (Almora)"},
    "Champawat": {"en": "Champawat", "hi": "चंपावत (Champawat)"},
    "Nainital": {"en": "Nainital", "hi": "नैनीताल (Nainital)"},
    "Udham Singh Nagar": {"en": "Udham Singh Nagar", "hi": "उधम सिंह नगर (Udham Singh Nagar)"}
}

ALL_DISTRICTS = list(DISTRICT_COORDINATES.keys())

# Quick Mapping Helpers for Bilingual Display
TYPE_HI_MAP = {
    "Flood": "बाढ़ (Flood)",
    "Landslide": "भूस्खलन (Landslide)",
    "Cloudburst": "बादल फटना (Cloudburst)",
    "Earthquake": "भूकंप (Earthquake)",
    "Forest Fire": "जंगल की आग (Forest Fire)",
    "Avalanche": "हिमस्खलन (Avalanche)",
    "Road Collapse": "सड़क धंसना (Road Collapse)",
    "Flash Flood": "फ्लैश फ्लड (Flash Flood)",
    "Building Collapse": "मकान ढहना (Building Collapse)"
}

SEV_HI_MAP = {
    "Critical": "अति-गंभीर (Critical)",
    "High": "गंभीर (High)",
    "Medium": "मध्यम (Medium)",
    "Low": "सामान्य (Low)"
}

STATUS_HI_MAP = {
    "Active": "सक्रिय (Active)",
    "Under Control": "नियंत्रण में (Under Control)",
    "Resolved": "समाधान हो गया (Resolved)"
}

@contextmanager
def get_connection():
    """Context manager for thread-safe SQLite connection handling."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def create_tables():
    """Create all required tables with indexes and bilingual columns."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Disasters Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disasters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                type_hi TEXT,
                location TEXT NOT NULL,
                location_hi TEXT,
                severity TEXT NOT NULL,
                severity_hi TEXT,
                description TEXT DEFAULT 'No details provided',
                description_hi TEXT,
                reporter_contact TEXT DEFAULT 'N/A',
                evidence_media TEXT DEFAULT '',
                latitude REAL,
                longitude REAL,
                date_reported TEXT NOT NULL,
                status TEXT DEFAULT 'Active',
                status_hi TEXT DEFAULT 'सक्रिय'
            )
        ''')

        
        # Resources Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                type_hi TEXT,
                name TEXT NOT NULL,
                name_hi TEXT,
                district TEXT NOT NULL,
                district_hi TEXT,
                quantity INTEGER NOT NULL,
                unit TEXT DEFAULT 'Units',
                unit_hi TEXT DEFAULT 'इकाइयां',
                available INTEGER DEFAULT 1
            )
        ''')
        
        # Shelters Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shelters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                name_hi TEXT,
                district TEXT NOT NULL,
                district_hi TEXT,
                capacity INTEGER NOT NULL,
                occupied INTEGER DEFAULT 0,
                contact TEXT NOT NULL,
                latitude REAL,
                longitude REAL
            )
        ''')
        
        # Hospitals Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                name_hi TEXT,
                district TEXT NOT NULL,
                district_hi TEXT,
                beds_total INTEGER NOT NULL,
                beds_available INTEGER NOT NULL,
                contact TEXT NOT NULL,
                latitude REAL,
                longitude REAL
            )
        ''')
        
        # Alerts Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disaster_id INTEGER,
                message TEXT NOT NULL,
                message_hi TEXT,
                severity TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                target TEXT DEFAULT 'All',
                FOREIGN KEY (disaster_id) REFERENCES disasters(id) ON DELETE CASCADE
            )
        ''')
        
        # Suggestions Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                title_hi TEXT,
                category TEXT NOT NULL,
                category_hi TEXT,
                description TEXT NOT NULL,
                description_hi TEXT,
                contributor TEXT DEFAULT 'Anonymous / नागरिक',
                district TEXT DEFAULT 'All Uttarakhand',
                district_hi TEXT DEFAULT 'समस्त उत्तराखंड',
                upvotes INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Under Review',
                status_hi TEXT DEFAULT 'समीक्षाधीन (Under Review)',
                created_at TEXT NOT NULL
            )
        ''')

        # Indexes for fast querying
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_disasters_status ON disasters(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_disasters_loc ON disasters(location)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_district ON resources(district)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shelters_district ON shelters(district)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hospitals_district ON hospitals(district)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_disaster_id ON alerts(disaster_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_suggestions_cat ON suggestions(category)")
        
        conn.commit()


def add_disaster(dtype, location, severity, description="Emergency incident reported", description_hi=None, reporter_contact="N/A", evidence_media="", lat=None, lon=None):
    """
    Insert disaster and auto-trigger bilingual emergency alert.
    """
    if lat is None or lon is None:
        coords = DISTRICT_COORDINATES.get(location, (30.0668, 79.0193))
        lat, lon = coords[0], coords[1]

    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    type_hi = TYPE_HI_MAP.get(dtype, dtype)
    loc_hi = DISTRICT_NAMES_MAP.get(location, {}).get("hi", location)
    sev_hi = SEV_HI_MAP.get(severity, severity)
    
    if not description_hi:
        description_hi = f"{loc_hi} में {type_hi} की घटना दर्ज की गई है। राहत दल पहुंच रहे हैं। ({description})"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO disasters (type, type_hi, location, location_hi, severity, severity_hi, description, description_hi, reporter_contact, evidence_media, latitude, longitude, date_reported, status, status_hi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', 'सक्रिय (Active)')
            """,
            (dtype, type_hi, location, loc_hi, severity, sev_hi, description, description_hi, reporter_contact, evidence_media, lat, lon, date_str)
        )
        disaster_id = cursor.lastrowid

        
        alert_en = f"EMERGENCY: {severity.upper()} {dtype} reported in {location}! Immediate caution advised."
        alert_hi = f"🚨 आपातकालीन अलर्ट: {loc_hi} जिले में {type_hi} की सूचना! सतर्क रहें व सुरक्षित स्थानों पर रहें।"
        cursor.execute(
            """
            INSERT INTO alerts (disaster_id, message, message_hi, severity, timestamp, target)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (disaster_id, alert_en, alert_hi, severity, date_str, "All")
        )
        conn.commit()
        return disaster_id

def add_custom_alert(disaster_id, message_en, message_hi=None, severity="High", target="All"):
    """Manually insert an administrative broadcast alert."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not message_hi:
        message_hi = message_en
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (disaster_id, message, message_hi, severity, timestamp, target)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (disaster_id, message_en, message_hi, severity, date_str, target)
        )
        conn.commit()
        return cursor.lastrowid

def get_all_disasters(status_filter=None, severity_filter=None, district_filter=None):
    """Retrieve all disasters with optional filtering."""
    query = "SELECT * FROM disasters WHERE 1=1"
    params = []
    
    if status_filter and status_filter != "All":
        query += " AND (status = ? OR status_hi LIKE ?)"
        params.extend([status_filter, f"%{status_filter}%"])
    if severity_filter and severity_filter != "All":
        query += " AND (severity = ? OR severity_hi LIKE ?)"
        params.extend([severity_filter, f"%{severity_filter}%"])
    if district_filter and district_filter != "All":
        query += " AND location = ?"
        params.append(district_filter)
        
    query += " ORDER BY id DESC"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def get_shelters_by_district(district=None):
    query = "SELECT * FROM shelters"
    params = []
    if district and district != "All":
        query += " WHERE district = ?"
        params.append(district)
    query += " ORDER BY name ASC"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def get_hospitals_by_district(district=None):
    query = "SELECT * FROM hospitals"
    params = []
    if district and district != "All":
        query += " WHERE district = ?"
        params.append(district)
    query += " ORDER BY name ASC"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def get_resources_by_district(district=None):
    query = "SELECT * FROM resources WHERE available = 1"
    params = []
    if district and district != "All":
        query += " AND district = ?"
        params.append(district)
    query += " ORDER BY type ASC, quantity DESC"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)


def get_all_alerts(limit=50):
    query = "SELECT * FROM alerts ORDER BY id DESC LIMIT ?"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=[limit])

def update_disaster_status(did, status):
    status_hi = STATUS_HI_MAP.get(status, status)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE disasters SET status = ?, status_hi = ? WHERE id = ?", (status, status_hi, did))
        if status == "Resolved":
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute(
                """
                INSERT INTO alerts (disaster_id, message, message_hi, severity, timestamp, target)
                VALUES (?, ?, ?, 'Low', ?, 'All')
                """,
                (
                    did,
                    f"UPDATE: Disaster #{did} has been marked RESOLVED by emergency authorities.",
                    f"🟢 समाधान अपडेट: घटना क्रमांक #{did} का राहत कार्य पूरा हो चुका है एवं स्थिति सुरक्षित घोषित कर दी गई है।",
                    date_str
                )
            )
        conn.commit()

def update_hospital_beds(hid, beds_available):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE hospitals SET beds_available = ? WHERE id = ?", (beds_available, hid))
        conn.commit()

def update_shelter_occupancy(sid, occupied):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE shelters SET occupied = ? WHERE id = ?", (occupied, sid))
        conn.commit()

def add_suggestion(title, category, description, contributor="Anonymous / नागरिक", district="All Uttarakhand", title_hi=None, category_hi=None, description_hi=None, district_hi=None):
    """Save a user suggestion to the database."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not title_hi:
        title_hi = title
    if not category_hi:
        category_hi = category
    if not description_hi:
        description_hi = description
    if not district_hi:
        district_hi = district

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO suggestions (title, title_hi, category, category_hi, description, description_hi, contributor, district, district_hi, upvotes, status, status_hi, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'Under Review', 'समीक्षाधीन (Under Review)', ?)
            """,
            (title, title_hi, category, category_hi, description, description_hi, contributor, district, district_hi, date_str)
        )
        conn.commit()
        return cursor.lastrowid

def get_all_suggestions(category_filter=None, district_filter=None, search_term=None):
    """Fetch all suggestions with optional filters."""
    query = "SELECT * FROM suggestions WHERE 1=1"
    params = []

    if category_filter and category_filter != "All" and category_filter != "सभी":
        query += " AND (category = ? OR category_hi LIKE ?)"
        params.extend([category_filter, f"%{category_filter}%"])
    if district_filter and district_filter != "All" and district_filter != "सभी":
        query += " AND (district = ? OR district_hi LIKE ?)"
        params.extend([district_filter, f"%{district_filter}%"])
    if search_term and search_term.strip():
        st_clean = f"%{search_term.strip()}%"
        query += " AND (title LIKE ? OR title_hi LIKE ? OR description LIKE ? OR description_hi LIKE ?)"
        params.extend([st_clean, st_clean, st_clean, st_clean])

    query += " ORDER BY upvotes DESC, id DESC"
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def upvote_suggestion(suggestion_id):
    """Increment the upvote count for a helpful suggestion."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE suggestions SET upvotes = upvotes + 1 WHERE id = ?", (suggestion_id,))
        conn.commit()

def update_suggestion_status(suggestion_id, new_status):
    """Admin review status updater for suggestions."""
    status_hi_map = {
        "Under Review": "समीक्षाधीन (Under Review)",
        "Approved / In Progress": "स्वीकृत व प्रगति पर (Approved / In Progress)",
        "Implemented": "लागू किया गया (Implemented)",
        "Closed": "बंद (Closed)"
    }
    status_hi = status_hi_map.get(new_status, new_status)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE suggestions SET status = ?, status_hi = ? WHERE id = ?", (new_status, status_hi, suggestion_id))
        conn.commit()

def edit_disaster(did, dtype, location, severity, description, status, reporter_contact="N/A", lat=None, lon=None):
    """Update all fields of an existing disaster incident."""
    type_hi = TYPE_HI_MAP.get(dtype, dtype)
    loc_hi = DISTRICT_NAMES_MAP.get(location, {}).get("hi", location)
    sev_hi = SEV_HI_MAP.get(severity, severity)
    status_hi = STATUS_HI_MAP.get(status, status)
    
    if lat is None or lon is None:
        coords = DISTRICT_COORDINATES.get(location, (30.0668, 79.0193))
        lat, lon = coords[0], coords[1]

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE disasters 
            SET type = ?, type_hi = ?, location = ?, location_hi = ?, severity = ?, severity_hi = ?, 
                description = ?, reporter_contact = ?, status = ?, status_hi = ?, latitude = ?, longitude = ?
            WHERE id = ?
            """,
            (dtype, type_hi, location, loc_hi, severity, sev_hi, description, reporter_contact, status, status_hi, lat, lon, did)
        )
        conn.commit()

def delete_disaster(did):
    """Delete a disaster record and its associated alerts."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alerts WHERE disaster_id = ?", (did,))
        cursor.execute("DELETE FROM disasters WHERE id = ?", (did,))
        conn.commit()

def dispatch_rescue_team(did, team_name, leader_name, leader_phone, personnel_count=15, notes="Rapid response deployment"):
    """Dispatch SDRF/NDRF rescue unit and post automated high-priority alert."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE disasters SET status = 'Under Control', status_hi = 'नियंत्रण में (Under Control)' WHERE id = ?", (did,))
        
        # Insert broadcast alert for dispatch
        msg_en = f"RESCUE DISPATCHED: {team_name} ({personnel_count} personnel under {leader_name}, Ph: {leader_phone}) deployed to incident #{did}. Notes: {notes}"
        msg_hi = f"🪖 राहत एवं बचाव दस्ता रवाना: {team_name} ({personnel_count} जवान, प्रभारी: {leader_name}, फोन: {leader_phone}) को घटना #{did} के लिए तैनात किया गया।"
        cursor.execute(
            """
            INSERT INTO alerts (disaster_id, message, message_hi, severity, timestamp, target)
            VALUES (?, ?, ?, 'High', ?, 'All')
            """,
            (did, msg_en, msg_hi, date_str)
        )
        conn.commit()

def add_hospital(name, name_hi, district, district_hi, beds_available, beds_total, contact, lat=None, lon=None):
    """Add a new hospital facility."""
    if lat is None or lon is None:
        coords = DISTRICT_COORDINATES.get(district, (30.0668, 79.0193))
        lat, lon = coords[0], coords[1]
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO hospitals (name, name_hi, district, district_hi, beds_available, beds_total, contact, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, name_hi, district, district_hi, beds_available, beds_total, contact, lat, lon)
        )
        conn.commit()
        return cursor.lastrowid

def edit_hospital(hid, name, name_hi, district, district_hi, beds_available, beds_total, contact, lat=None, lon=None):
    """Update hospital facility details."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE hospitals
            SET name = ?, name_hi = ?, district = ?, district_hi = ?, beds_available = ?, beds_total = ?, contact = ?, latitude = COALESCE(?, latitude), longitude = COALESCE(?, longitude)
            WHERE id = ?
            """,
            (name, name_hi, district, district_hi, beds_available, beds_total, contact, lat, lon, hid)
        )
        conn.commit()

def delete_hospital(hid):
    """Remove a hospital record."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hospitals WHERE id = ?", (hid,))
        conn.commit()

def add_shelter(name, name_hi, district, district_hi, capacity, occupied, contact, lat=None, lon=None):
    """Add a new relief shelter."""
    if lat is None or lon is None:
        coords = DISTRICT_COORDINATES.get(district, (30.0668, 79.0193))
        lat, lon = coords[0], coords[1]
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO shelters (name, name_hi, district, district_hi, capacity, occupied, contact, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, name_hi, district, district_hi, capacity, occupied, contact, lat, lon)
        )
        conn.commit()
        return cursor.lastrowid

def edit_shelter(sid, name, name_hi, district, district_hi, capacity, occupied, contact, lat=None, lon=None):
    """Update relief shelter details."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE shelters
            SET name = ?, name_hi = ?, district = ?, district_hi = ?, capacity = ?, occupied = ?, contact = ?, latitude = COALESCE(?, latitude), longitude = COALESCE(?, longitude)
            WHERE id = ?
            """,
            (name, name_hi, district, district_hi, capacity, occupied, contact, lat, lon, sid)
        )
        conn.commit()

def delete_shelter(sid):
    """Remove a relief shelter."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shelters WHERE id = ?", (sid,))
        conn.commit()

def add_resource(type, type_hi, name, name_hi, district, district_hi, quantity, unit="Units", unit_hi="इकाइयां", available=1):
    """Add a new stockpile / relief supply."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO resources (type, type_hi, name, name_hi, district, district_hi, quantity, unit, unit_hi, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (type, type_hi, name, name_hi, district, district_hi, quantity, unit, unit_hi, available)
        )
        conn.commit()
        return cursor.lastrowid

def edit_resource(rid, name, quantity, available=1):
    """Update resource stockpile quantity."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE resources SET name = ?, quantity = ?, available = ? WHERE id = ?", (name, quantity, available, rid))
        conn.commit()

def delete_resource(rid):
    """Delete a resource stockpile entry."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM resources WHERE id = ?", (rid,))
        conn.commit()

def delete_alert(aid):
    """Withdraw or delete a broadcast alert."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alerts WHERE id = ?", (aid,))
        conn.commit()

def delete_suggestion(sug_id):
    """Delete a citizen suggestion."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM suggestions WHERE id = ?", (sug_id,))
        conn.commit()

def drop_and_recreate_tables():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS alerts")
        cursor.execute("DROP TABLE IF EXISTS resources")
        cursor.execute("DROP TABLE IF EXISTS hospitals")
        cursor.execute("DROP TABLE IF EXISTS shelters")
        cursor.execute("DROP TABLE IF EXISTS disasters")
        cursor.execute("DROP TABLE IF EXISTS suggestions")
        conn.commit()
    create_tables()

def clear_all_data():
    drop_and_recreate_tables()


def get_dashboard_summary():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM disasters WHERE status = 'Active'")
        active_disasters = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM disasters")
        total_disasters = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM disasters WHERE status = 'Active' AND severity = 'Critical'")
        critical_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM disasters WHERE status = 'Active' AND severity = 'High'")
        high_count = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(beds_available), 0), COALESCE(SUM(beds_total), 0) FROM hospitals")
        h_row = cursor.fetchone()
        beds_avail, beds_total = h_row[0], h_row[1]
        cursor.execute("SELECT COALESCE(SUM(occupied), 0), COALESCE(SUM(capacity), 0) FROM shelters")
        s_row = cursor.fetchone()
        shelter_occ, shelter_cap = s_row[0], s_row[1]
        
        return {
            "active_disasters": active_disasters,
            "total_disasters": total_disasters,
            "critical_count": critical_count,
            "high_count": high_count,
            "beds_available": beds_avail,
            "beds_total": beds_total,
            "shelter_occupied": shelter_occ,
            "shelter_capacity": shelter_cap
        }

