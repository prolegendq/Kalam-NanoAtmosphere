import streamlit as st
from datetime import datetime
from src.data_engine.city_profiles import *

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
if not st.session_state.get("logged_in"):
    st.error("Please log in from the Home page to use Kalam NanoAtmosphere.")
    st.stop()
st.title("National Reports: City Snapshot")

st.write(
    "Kalam NanoAtmosphere aggregates satellite gases into a quick national snapshot. "
    "Values are indicative means over the last month."
)

rows = []
min_v, max_v = 0.00005, 0.00025

for city, g in CITY_GASES.items():
    no2 = g["NO2"]
    # Simple city-level Breathability from NO2
    norm = max(0.0, min(1.0, (no2 - min_v) / (max_v - min_v)))
    breathe = (1 - norm) * 100

    if breathe >= 80:
        status = "Healthy"
    elif breathe >= 60:
        status = "Caution"
        # below 60 unhealthy
    else:
        status = "Unhealthy"

    rows.append(
        {
            "City": city,
            "NO₂ (mol/m²)": f"{no2:.1e}",
            "SO₂ (mol/m²)": f"{g['SO2']:.1e}",
            "CO (mol/m²)": f"{g['CO']:.2f}",
            "Breathability": f"{breathe:.0f}/100",
            "Status": status,
        }
    )

st.dataframe(rows, use_container_width=True)