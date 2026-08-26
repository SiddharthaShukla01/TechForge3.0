"""
weather.py — Live Weather & Weather Alert System for Uttarakhand Disaster Portal
Uses Open-Meteo API (free, no API key required) + Open-Meteo Geocoding
Covers all 13 districts with real-time conditions + WMO weather alert thresholds.
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

# ── District coordinates (lat, lon) ─────────────────────────────────────────
DISTRICT_WEATHER_COORDS = {
    "Dehradun":         (30.3165, 78.0322),
    "Haridwar":         (29.9457, 78.1642),
    "Tehri Garhwal":    (30.3800, 78.4800),
    "Chamoli":          (30.5500, 79.5667),
    "Uttarkashi":       (30.7268, 78.4354),
    "Rudraprayag":      (30.2844, 78.9811),
    "Pauri Garhwal":    (30.1500, 78.7800),
    "Pithoragarh":      (29.5828, 80.2182),
    "Bageshwar":        (29.8406, 79.7694),
    "Almora":           (29.5971, 79.6591),
    "Champawat":        (29.3347, 80.0911),
    "Nainital":         (29.3919, 79.4542),
    "Udham Singh Nagar":(28.9800, 79.4000),
}

# ── WMO Weather Interpretation Codes ────────────────────────────────────────
WMO_DESCRIPTIONS = {
    0:  {"en": "Clear sky", "hi": "साफ आकाश", "icon": "☀️"},
    1:  {"en": "Mainly clear", "hi": "मुख्यतः साफ", "icon": "🌤️"},
    2:  {"en": "Partly cloudy", "hi": "आंशिक बादल", "icon": "⛅"},
    3:  {"en": "Overcast", "hi": "पूरी तरह बादल", "icon": "☁️"},
    45: {"en": "Fog", "hi": "कोहरा", "icon": "🌫️"},
    48: {"en": "Icy fog", "hi": "बर्फीला कोहरा", "icon": "🌫️❄️"},
    51: {"en": "Light drizzle", "hi": "हल्की बूंदाबांदी", "icon": "🌦️"},
    53: {"en": "Moderate drizzle", "hi": "मध्यम बूंदाबांदी", "icon": "🌦️"},
    55: {"en": "Heavy drizzle", "hi": "भारी बूंदाबांदी", "icon": "🌧️"},
    61: {"en": "Slight rain", "hi": "हल्की बारिश", "icon": "🌧️"},
    63: {"en": "Moderate rain", "hi": "मध्यम बारिश", "icon": "🌧️"},
    65: {"en": "Heavy rain", "hi": "भारी बारिश", "icon": "🌧️⚠️"},
    71: {"en": "Slight snowfall", "hi": "हल्की बर्फबारी", "icon": "🌨️"},
    73: {"en": "Moderate snowfall", "hi": "मध्यम बर्फबारी", "icon": "❄️"},
    75: {"en": "Heavy snowfall", "hi": "भारी बर्फबारी", "icon": "❄️⚠️"},
    77: {"en": "Snow grains", "hi": "बर्फ के कण", "icon": "🌨️"},
    80: {"en": "Slight rain showers", "hi": "हल्की बौछारें", "icon": "🌦️"},
    81: {"en": "Moderate rain showers", "hi": "मध्यम बौछारें", "icon": "🌧️"},
    82: {"en": "Violent rain showers", "hi": "तेज बौछारें", "icon": "⛈️⚠️"},
    85: {"en": "Slight snow showers", "hi": "हल्की हिम बौछारें", "icon": "🌨️"},
    86: {"en": "Heavy snow showers", "hi": "भारी हिम बौछारें", "icon": "❄️⚠️"},
    95: {"en": "Thunderstorm", "hi": "तूफान व बिजली", "icon": "⛈️🚨"},
    96: {"en": "Thunderstorm with hail", "hi": "ओलावृष्टि सहित तूफान", "icon": "⛈️🌩️"},
    99: {"en": "Thunderstorm with heavy hail", "hi": "भारी ओलावृष्टि सहित तूफान", "icon": "⛈️🚨"},
}

# ── Alert thresholds (Uttarakhand disaster-relevant) ─────────────────────────
ALERT_RULES = [
    # (condition_fn, severity, en_msg_fn, hi_msg_fn)
    (
        lambda w: w.get("precipitation_sum", 0) > 100,
        "Critical",
        lambda d, w: f"Extremely heavy rainfall ({w['precipitation_sum']:.0f} mm expected) in {d}. High risk of cloudbursts, flash floods and landslides. Evacuate vulnerable areas immediately.",
        lambda d, w: f"{d} में अत्यधिक भारी वर्षा ({w['precipitation_sum']:.0f} मिमी अनुमानित)। बादल फटने, फ्लैश फ्लड और भूस्खलन का खतरा। कमज़ोर क्षेत्रों से तत्काल निकासी करें।",
    ),
    (
        lambda w: 50 < w.get("precipitation_sum", 0) <= 100,
        "High",
        lambda d, w: f"Heavy rainfall alert ({w['precipitation_sum']:.0f} mm) in {d}. Risk of landslides and road blockages. Avoid hill roads.",
        lambda d, w: f"{d} में भारी वर्षा चेतावनी ({w['precipitation_sum']:.0f} मिमी)। भूस्खलन और सड़क बाधा का खतरा। पहाड़ी सड़कों से बचें।",
    ),
    (
        lambda w: w.get("weathercode", 0) in (95, 96, 99),
        "Critical",
        lambda d, w: f"Severe thunderstorm with lightning/hail active in {d}. Seek shelter immediately. Avoid open areas.",
        lambda d, w: f"{d} में भारी तूफान, बिजली और ओलावृष्टि। तत्काल सुरक्षित स्थान पर जाएं। खुले स्थानों से बचें।",
    ),
    (
        lambda w: w.get("wind_speed_max", 0) > 60,
        "High",
        lambda d, w: f"Strong winds ({w['wind_speed_max']:.0f} km/h) forecast in {d}. Risk of tree fall and structure damage.",
        lambda d, w: f"{d} में तेज हवाएं ({w['wind_speed_max']:.0f} किमी/घंटा)। पेड़ गिरने और संरचना क्षति का खतरा।",
    ),
    (
        lambda w: w.get("temperature_max", 20) > 42,
        "High",
        lambda d, w: f"Heatwave alert in {d}: Max temperature {w['temperature_max']:.1f}°C. Avoid outdoor exposure between 11am–4pm.",
        lambda d, w: f"{d} में लू चेतावनी: अधिकतम तापमान {w['temperature_max']:.1f}°C। सुबह 11 बजे से शाम 4 बजे के बीच बाहर निकलने से बचें।",
    ),
    (
        lambda w: w.get("temperature_min", 10) < 0,
        "Medium",
        lambda d, w: f"Freezing temperature ({w['temperature_min']:.1f}°C) in {d}. High altitude routes may be icy. Snowfall risk.",
        lambda d, w: f"{d} में हिमांक तापमान ({w['temperature_min']:.1f}°C)। ऊंचाई के रास्ते बर्फीले हो सकते हैं।",
    ),
    (
        lambda w: w.get("snowfall_sum", 0) > 10,
        "High",
        lambda d, w: f"Heavy snowfall ({w['snowfall_sum']:.0f} cm) expected in {d}. High altitude roads may close. Risk of avalanche.",
        lambda d, w: f"{d} में भारी बर्फबारी ({w['snowfall_sum']:.0f} सेमी) संभावित। ऊंचे रास्ते बंद हो सकते हैं। हिमस्खलन का खतरा।",
    ),
    (
        lambda w: 20 < w.get("precipitation_sum", 0) <= 50,
        "Medium",
        lambda d, w: f"Moderate to heavy rain ({w['precipitation_sum']:.0f} mm) expected in {d}. Stay alert for local flooding.",
        lambda d, w: f"{d} में मध्यम से भारी वर्षा ({w['precipitation_sum']:.0f} मिमी) अनुमानित। स्थानीय बाढ़ के लिए सतर्क रहें।",
    ),
]


def _fetch_json(url: str, timeout: int = 8) -> dict:
    """Simple JSON fetch with timeout — no external dependencies."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "UttarakhandDisasterPortal/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def fetch_current_weather(district: str) -> dict:
    """
    Fetch today's weather + 3-day forecast for a district.
    Returns a dict with keys: current, today, forecast (list of 3 days), alerts, error.
    """
    if district not in DISTRICT_WEATHER_COORDS:
        return {"error": f"Unknown district: {district}"}

    lat, lon = DISTRICT_WEATHER_COORDS[district]

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"precipitation,weathercode,windspeed_10m,winddirection_10m,uv_index"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min,"
        f"precipitation_sum,snowfall_sum,windspeed_10m_max,uv_index_max"
        f"&timezone=Asia%2FKolkata"
        f"&forecast_days=4"
    )

    data = _fetch_json(url)
    if "error" in data and "current" not in data:
        return {"error": data["error"], "district": district}

    try:
        cur = data["current"]
        daily = data["daily"]
        wmo_code = int(cur.get("weathercode", 0))
        wmo_info = WMO_DESCRIPTIONS.get(wmo_code, {"en": "Unknown", "hi": "अज्ञात", "icon": "🌡️"})

        current = {
            "temperature":    cur.get("temperature_2m"),
            "feels_like":     cur.get("apparent_temperature"),
            "humidity":       cur.get("relative_humidity_2m"),
            "precipitation":  cur.get("precipitation"),
            "windspeed":      cur.get("windspeed_10m"),
            "winddirection":  cur.get("winddirection_10m"),
            "uv_index":       cur.get("uv_index"),
            "weathercode":    wmo_code,
            "condition_en":   wmo_info["en"],
            "condition_hi":   wmo_info["hi"],
            "icon":           wmo_info["icon"],
            "updated_at":     cur.get("time", datetime.now().strftime("%Y-%m-%dT%H:%M")),
        }

        # Build forecast for next 4 days (index 0 = today)
        forecast = []
        for i in range(min(4, len(daily["time"]))):
            day_code = int(daily["weathercode"][i])
            day_wmo = WMO_DESCRIPTIONS.get(day_code, {"en": "Unknown", "hi": "अज्ञात", "icon": "🌡️"})
            forecast.append({
                "date":             daily["time"][i],
                "weathercode":      day_code,
                "condition_en":     day_wmo["en"],
                "condition_hi":     day_wmo["hi"],
                "icon":             day_wmo["icon"],
                "temperature_max":  daily["temperature_2m_max"][i],
                "temperature_min":  daily["temperature_2m_min"][i],
                "precipitation_sum": daily["precipitation_sum"][i],
                "snowfall_sum":     daily["snowfall_sum"][i],
                "wind_speed_max":   daily["windspeed_10m_max"][i],
                "uv_index_max":     daily["uv_index_max"][i],
            })

        # Generate weather alerts from today's + tomorrow's forecast
        alerts = []
        for day_data in forecast[:2]:  # Today + tomorrow
            for (cond_fn, severity, en_fn, hi_fn) in ALERT_RULES:
                try:
                    if cond_fn(day_data):
                        when = "Today" if day_data["date"] == forecast[0]["date"] else "Tomorrow"
                        when_hi = "आज" if when == "Today" else "कल"
                        alerts.append({
                            "severity":   severity,
                            "when":       when,
                            "when_hi":    when_hi,
                            "date":       day_data["date"],
                            "message_en": f"[{when}] " + en_fn(district, day_data),
                            "message_hi": f"[{when_hi}] " + hi_fn(district, day_data),
                        })
                except Exception:
                    pass

        # Deduplicate by severity+when
        seen = set()
        unique_alerts = []
        for a in alerts:
            key = (a["severity"], a["when"], a["message_en"][:40])
            if key not in seen:
                seen.add(key)
                unique_alerts.append(a)

        return {
            "district":   district,
            "lat":        lat,
            "lon":        lon,
            "current":    current,
            "today":      forecast[0] if forecast else {},
            "forecast":   forecast[1:],   # days 1-3
            "alerts":     unique_alerts,
            "error":      None,
        }

    except Exception as e:
        return {"error": str(e), "district": district}


def fetch_all_districts_summary() -> list[dict]:
    """
    Fetch a lightweight summary (current temp + weathercode + alerts) for all 13 districts.
    Used for the map overview panel.
    """
    results = []
    for district in DISTRICT_WEATHER_COORDS:
        lat, lon = DISTRICT_WEATHER_COORDS[district]
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,weathercode,precipitation,windspeed_10m"
            f"&daily=precipitation_sum,snowfall_sum,windspeed_10m_max,weathercode,temperature_2m_max,temperature_2m_min"
            f"&timezone=Asia%2FKolkata&forecast_days=2"
        )
        data = _fetch_json(url)
        if "error" in data and "current" not in data:
            results.append({"district": district, "error": data.get("error", "fetch failed")})
            continue

        try:
            cur = data["current"]
            daily = data["daily"]
            wmo_code = int(cur.get("weathercode", 0))
            wmo_info = WMO_DESCRIPTIONS.get(wmo_code, {"en": "Unknown", "hi": "अज्ञात", "icon": "🌡️"})

            today = {
                "date":             daily["time"][0],
                "weathercode":      int(daily["weathercode"][0]),
                "temperature_max":  daily["temperature_2m_max"][0],
                "temperature_min":  daily["temperature_2m_min"][0],
                "precipitation_sum": daily["precipitation_sum"][0],
                "snowfall_sum":     daily["snowfall_sum"][0],
                "wind_speed_max":   daily["windspeed_10m_max"][0],
            }

            # Check alerts
            has_alert = False
            alert_severity = None
            for (cond_fn, severity, _, _) in ALERT_RULES:
                try:
                    if cond_fn(today):
                        has_alert = True
                        alert_severity = severity
                        break  # highest priority rule first
                except Exception:
                    pass

            results.append({
                "district":       district,
                "temperature":    cur.get("temperature_2m"),
                "weathercode":    wmo_code,
                "condition_en":   wmo_info["en"],
                "condition_hi":   wmo_info["hi"],
                "icon":           wmo_info["icon"],
                "precipitation":  cur.get("precipitation", 0),
                "windspeed":      cur.get("windspeed_10m", 0),
                "has_alert":      has_alert,
                "alert_severity": alert_severity,
                "error":          None,
            })
        except Exception as e:
            results.append({"district": district, "error": str(e)})

    return results


def wind_direction_label(degrees, lang="en") -> str:
    """Convert wind degrees to compass label."""
    dirs_en = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    dirs_hi = ["उत्तर", "उत्तर-पूर्व", "पूर्व", "दक्षिण-पूर्व", "दक्षिण", "दक्षिण-पश्चिम", "पश्चिम", "उत्तर-पश्चिम"]
    idx = round(degrees / 45) % 8
    return dirs_hi[idx] if lang == "hi" else dirs_en[idx]


def uv_label(uv, lang="en") -> str:
    """Human-readable UV index label."""
    if uv is None:
        return "N/A"
    if uv <= 2:
        return ("कम (Low)" if lang == "hi" else "Low")
    elif uv <= 5:
        return ("मध्यम (Moderate)" if lang == "hi" else "Moderate")
    elif uv <= 7:
        return ("उच्च (High)" if lang == "hi" else "High")
    elif uv <= 10:
        return ("बहुत उच्च (Very High)" if lang == "hi" else "Very High")
    else:
        return ("अत्यधिक (Extreme)" if lang == "hi" else "Extreme")
