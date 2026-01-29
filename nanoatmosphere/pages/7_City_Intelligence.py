import streamlit as st
from datetime import datetime
from src.data_engine.city_profiles import CITY_GASES, interpret_city

# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")
if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

# Log with CONSISTENT keys
st.session_state.user_logs.append({
    "user": st.session_state.get("user_email", "guest"),
    "action": "Page visited",
    "page": "city intelligence",  # Change per page
    "timestamp": datetime.now().strftime("%H:%M:%S")
})
st.title("City Intelligence: Multi-Gas Profiles")

st.write(
    "Kalam NanoAtmosphere builds a chemical fingerprint for each city using Sentinel‑5P gases."
)

# 1) Select city
city = st.selectbox("Select a city", list(CITY_GASES.keys()))

gases = CITY_GASES[city]

# 2) Show gas metrics
st.subheader(f"{city} – Gas Fingerprint")

c1, c2, c3 = st.columns(3)
c1.metric("NO₂ (traffic)", f"{gases['NO2']:.1e} mol/m²")
c2.metric("SO₂ (industry)", f"{gases['SO2']:.1e} mol/m²")
c3.metric("CO (combustion)", f"{gases['CO']:.2f} mol/m²")

# 3) Kalam NanoAtmosphere observations
st.markdown(
    """
    <h2 style='text-align: center;'>
        <span style='color: #FBD85B;'>Nano</span><span style='color: #56D5F2;'>Atmosphere</span> Observations
    </h2>
    """,
    unsafe_allow_html=True
)
notes = interpret_city(gases)
# Simple dominant source tag based on largest normalized gas
no2, so2, co = gases["NO2"], gases["SO2"], gases["CO"]
max_gas = max([("NO₂", no2), ("SO₂", so2), ("CO", co)], key=lambda x: x[1])[0]

st.caption(f"Dominant signal in {city}: **{max_gas}‑driven pollution signature.**")

for i, note in enumerate(notes, start=1):
    st.write(f"{i}. {note}")