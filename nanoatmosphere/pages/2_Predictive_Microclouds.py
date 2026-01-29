import streamlit as st
from datetime import datetime
from src.data_engine.no2_sampler import get_no2_at_latlon

if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

# Log with CONSISTENT keys
st.session_state.user_logs.append({
    "user": st.session_state.get("user_email", "guest"),
    "action": "Page visited",
    "page": "Predicive micro clouds",  # Change per page
    "timestamp": datetime.now().strftime("%H:%M:%S")
})

# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")
st.title("Predictive Micro‑Cloud Engine")

st.caption(
    "Given a Sentinel‑5P NO₂ micro‑cloud, Kalam NanoAtmosphere estimates how breathable "
    "this spot of the city is right now and how risky it is for people on the ground."
)


if "clicked_point" not in st.session_state:
    st.warning("Go to the God‑Eye map and click a location first.")
else:
    lat, lon = st.session_state["clicked_point"]
    st.info(f"Analyzing micro‑zone at {lat:.4f}, {lon:.4f}")

    no2_val = get_no2_at_latlon(lat, lon)
    # Simple Breathability Index (you can improve later):
    # assume 0.00005 = perfect, 0.00025 = worst
    min_v, max_v = 0.00005, 0.00025
    norm = max(0.0, min(1.0, (no2_val - min_v) / (max_v - min_v)))
    breathability = (1 - norm) * 100

    risk = "Low"
    if breathability < 80:
        risk = "Medium"
    if breathability < 60:
        risk = "High"

    c1, c2, c3 = st.columns(3)
    c1.metric("Breathability Index", f"{breathability:.0f}/100")
    c2.metric("Risk Level", risk)
    c3.metric("NO₂ (mol/m²)", f"{no2_val:.1e}")
layer = st.session_state.get("time_layer", "Recent")
no2_val = get_no2_at_latlon(lat, lon, layer)
with st.expander("What does this mean?"):
    st.markdown(
        f"""
        - A Breathability Index of **{breathability:.0f}/100** means air is 
          {'relatively safe for most people' if breathability >= 80 else 'showing stress for sensitive groups'} in this micro‑zone.
        - Current NO₂ is **{no2_val:.1e} mol/m²**, derived from Sentinel‑5P for this 1 km tile.
        - Risk Level **{risk}** combines NO₂ with simple thresholds you can tune later.
        """
    )
with st.expander("How to read these numbers?"):
    st.markdown("""
        - **Breathability Index** behaves like a mini‑AQI: values near 100 mean cleaner, easier‑to‑breathe air; low scores mean stressed air quality.
        - **Risk Level** mirrors public AQI language: Low ≈ generally acceptable, Medium ≈ sensitive groups should be careful, High ≈ unhealthy for many people.
        - NO₂ is strongly linked with road traffic; higher values are associated with more asthma attacks and lung irritation for children and older adults.
        """)

st.markdown(
    """
    **Kalam NanoAtmosphere legend**

    - 80–100: Healthy air for most people (Low risk).
    - 60–79: Caution; sensitive groups may feel effects (Medium risk).
    - 0–59: Unhealthy; limit exposure for everyone (High risk).
    """
)