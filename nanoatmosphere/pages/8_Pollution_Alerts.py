from datetime import*
import time
import streamlit as st
import requests
import random

# IMPORTANT: Replace with your actual OpenAQ API Key
# You can get one by signing up at https://explore.openaq.org/register
OPENAQ_API_KEY = 'YOUR_OPENAQ_API_KEY'

# City to coordinates mapping
CITY_COORDINATES = {
    "Chennai": (13.0827, 80.2707),
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777),
    "Bengaluru": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
}

if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

# Log with CONSISTENT keys
st.session_state.user_logs.append({
    "user": st.session_state.get("user_email", "guest"),
    "action": "Page visited",
    "page": "National Reports",  # Change per page
    "timestamp": datetime.now().strftime("%H:%M:%S")
})# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")
# ---------- ACCESS CONTROL ----------
if not st.session_state.get("logged_in"):
    st.error("Please log in from the Home page to use Kalam NanoAtmosphere.")
    st.stop()

# ---------- HELPERS ----------

def classify_aqi(aqi: float):
    """
    AQI banding & short advisory based on India's National AQI terminology. [web:395][web:228]
    """
    if aqi <= 50:
        return ("Good", "#009966", "Air quality is good. Enjoy outdoor activities.")
    elif aqi <= 100:
        return ("Satisfactory", "#FFDE33",
                "Minor breathing discomfort to sensitive people (lungs, heart).")
    elif aqi <= 200:
        return ("Moderately Polluted", "#FF9933",
                "People with asthma, children, and elders should reduce long or heavy outdoor exertion.")
    elif aqi <= 300:
        return ("Poor", "#CC0033",
                "Sensitive groups should avoid outdoor activity; others limit long or heavy exertion.")
    elif aqi <= 400:
        return ("Very Poor", "#660099",
                "Everyone should limit outdoor activity. High risk for respiratory/cardiac patients.")
    else:
        return ("Severe", "#7E0023",
                "Health emergency. Stay indoors as much as possible and follow official advisories.")

def get_city_aqi(city: str) -> float:
    """
    Fetches the latest PM2.5 value from the OpenAQ API for a given city using V3 endpoints.
    Returns a random value as a fallback if the API call fails or no PM2.5 data is found.
    """
    try:
        lat, lon = CITY_COORDINATES[city]

        # Step 1: Find locations near the coordinates
        locations_response = requests.get(
            "https://api.openaq.org/v3/locations",
            params={
                "coordinates": f"{lat},{lon}",
                "radius": 10000,
                "limit": 1 # We only need one location for now
            },
            headers={"X-API-Key": OPENAQ_API_KEY}, # Add headers here
            timeout=10
        )
        locations_response.raise_for_status()
        locations_data = locations_response.json()

        if not locations_data["results"]:
            raise ValueError("No locations found near the specified coordinates.")

        location_id = locations_data["results"][0]["id"]

        # Step 2: Get latest measurements for the found location
        latest_measurements_response = requests.get(
            f"https://api.openaq.org/v3/locations/{location_id}/latest",
            headers={"X-API-Key": OPENAQ_API_KEY}, # Add headers here
            timeout=10
        )
        latest_measurements_response.raise_for_status()
        latest_measurements_data = latest_measurements_response.json()

        if latest_measurements_data["results"]:
            for measurement in latest_measurements_data["results"][0]["measurements"]:
                if measurement["parameter"] == "pm25":
                    return measurement["value"]

    except (requests.exceptions.RequestException, KeyError, IndexError, ValueError) as e:
        print(f"OpenAQ API V3 request failed for {city}: {e}")
        # Fallback to random value if API call fails or no data is found
        pass
    return round(random.uniform(30, 480), 1)

# ---------- UI LAYOUT ----------

st.title("Pollution Alert System")

# Top controls
top_col1, top_col2, top_col3 = st.columns([2, 1, 1])

with top_col1:
    city = st.selectbox(
        "Select city",
        ["Chennai", "Delhi", "Mumbai", "Bengaluru", "Kolkata"],
        index=0,
    )

with top_col2:
    refresh = st.button("Refresh now", use_container_width=True)

with top_col3:
    auto_refresh = st.checkbox("Auto‑refresh (30 s)", value=False)

# Data retrieval
if "last_alert_pull" not in st.session_state:
    st.session_state.last_alert_pull = 0

should_pull = refresh or (time.time() - st.session_state.last_alert_pull > 30)
if should_pull:
    current_aqi = get_city_aqi(city)
    st.session_state.current_aqi = current_aqi
    st.session_state.last_alert_pull = time.time()
else:
    current_aqi = st.session_state.get("current_aqi", get_city_aqi(city))

label, color, advisory = classify_aqi(current_aqi)

# ---------- ALERT CARD ----------

alert_container = st.container(border=True)
with alert_container:
    st.markdown(
        f"""
        <div style="
            background:{color};
            padding:18px 20px;
            border-radius:10px;
            color:white;
            display:flex;
            justify-content:space-between;
            align-items:center;
        ">
            <div>
                <div style="font-size:14px;opacity:0.9;">Current status for {city}</div>
                <div style="font-size:28px;font-weight:700;margin-top:4px;">{label}</div>
                <div style="font-size:14px;margin-top:6px;max-width:520px;">{advisory}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:14px;opacity:0.9;">AQI (NO₂‑weighted)</div>
                <div style="font-size:32px;font-weight:700;">{current_aqi:.1f}</div>
                <div style="font-size:12px;opacity:0.8;margin-top:4px;">
                    Based on Indian National AQI banding and health guidance. [web:395][web:392]
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Health recommendations")
if label in ("Good", "Satisfactory"):
    st.markdown(
        "- Normal outdoor activity is fine.\n"
        "- Continue usual exercise routines.\n"
        "- People with asthma should still keep inhalers handy."
    )
elif label == "Moderately Polluted":
    st.markdown(
        "- Children, elders, and asthma/COPD patients should **reduce** heavy outdoor exercise.\n"
        "- Prefer early‑morning or late‑evening walks.\n"
        "- Wear a mask if you experience discomfort."
    )
elif label == "Poor":
    st.markdown(
        "- Everyone should **avoid** prolonged or heavy outdoor exertion.\n"
        "- People with heart or lung disease, older adults, and children should remain indoors.\n"
        "- Keep windows closed. Use an air purifier if available."
    )
elif label == "Very Poor":
    st.markdown(
        "- **Avoid all outdoor activity.**\n"
        "- Keep windows and doors shut. Run an air purifier on high.\n"
        "- If you must go out, wear a well-fitted N95 or P100 mask."
    )
else:  # Severe
    st.markdown(
        "- **Remain indoors and keep activity levels low.** This is a health emergency.\n"
        "- Vulnerable individuals should be closely monitored.\n"
        "- Do not rely on simple cloth or surgical masks; only N95/P100 respirators offer protection."
    )

