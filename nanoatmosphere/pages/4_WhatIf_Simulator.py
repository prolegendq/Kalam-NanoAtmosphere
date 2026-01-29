import streamlit as st
from datetime import datetime
from src.data_engine.no2_sampler import get_no2_at_latlon

# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")
if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

# Log with CONSISTENT keys
st.session_state.user_logs.append({
    "user": st.session_state.get("user_email", "guest"),
    "action": "Page visited",
    "page": "Whatif",  # Change per page
    "timestamp": datetime.now().strftime("%H:%M:%S")
})
st.title("What‑If Simulator: Policy Impact")

st.write(
    "Kalam NanoAtmosphere lets you test policy packages on this micro‑zone and see how "
    "NO₂ and the Breathability Index respond in real time."
)

# 1) Ensure a micro‑zone is selected
if "clicked_point" not in st.session_state:
    st.warning("Go to the God‑Eye map and click a location first.")
    st.stop()

lat, lon = st.session_state["clicked_point"]
st.info(f"Analyzing micro‑zone at {lat:.4f}, {lon:.4f}")

# 2) Get baseline NO2 and Breathability
no2_base = get_no2_at_latlon(lat, lon)

# Same simple Breathability formula you used in Predictive page
min_v, max_v = 0.00005, 0.00025
norm_base = max(0.0, min(1.0, (no2_base - min_v) / (max_v - min_v)))
breathe_base = (1 - norm_base) * 100

col_base1, col_base2 = st.columns(2)
col_base1.metric("Baseline NO₂", f"{no2_base:.1e} mol/m²")
col_base2.metric("Baseline Breathability", f"{breathe_base:.0f}/100")

st.markdown("---")

# 3) Policy sliders (impact assumptions in % NO2 reduction)
st.subheader("Policy Levers")

col1, col2, col3 = st.columns(3)

trees = col1.slider(
    "Urban trees / green buffers (units)",
    min_value=0,
    max_value=2000,
    value=500,
    step=100,
)
buses = col2.slider(
    "Electric / low‑emission buses (lines)",
    min_value=0,
    max_value=50,
    value=10,
    step=5,
)
trucks = col3.slider(
    "Truck‑time restrictions (hours/day)",
    min_value=0,
    max_value=12,
    value=4,
    step=1,
)

# 4) Convert policies to NO2 reduction (simple illustrative math)
# You can tweak these coefficients to change strength.
reduction_trees = 0.00000001 * trees      # 1e‑11 per tree unit
reduction_buses = 0.00000005 * buses      # 5e‑10 per bus line
reduction_trucks = 0.0000001 * trucks     # 1e‑9 per restricted hour

total_reduction = reduction_trees + reduction_buses + reduction_trucks

no2_new = max(no2_base - total_reduction, 0.0)

norm_new = max(0.0, min(1.0, (no2_new - min_v) / (max_v - min_v)))
breathe_new = (1 - norm_new) * 100

improvement = breathe_new - breathe_base

# 5) Show results
st.subheader("Simulated Outcome")

c1, c2, c3 = st.columns(3)
c1.metric("Simulated NO₂", f"{no2_new:.1e} mol/m²", delta=f"{no2_new-no2_base:.1e}")
c2.metric(
    "Breathability Index",
    f"{breathe_new:.0f}/100",
    delta=f"{improvement:+.0f}",
)
c3.metric(
    "Total Policy Effect",
    f"{total_reduction:.1e} mol/m² NO₂ reduction",
)
if breathe_new >= 80:
    label = "Healthy"
elif breathe_new >= 60:
    label = "Caution"
else:
    label = "Unhealthy"
if breathe_new >= 80:
    scenario = "Safe"
elif breathe_new >= 60:
    scenario = "Improved but caution"
else:
    scenario = "Still unsafe"

st.write(f"Kalam NanoAtmosphere rates this scenario as: **{scenario} air quality**.")
st.write(f"Kalam NanoAtmosphere rating for this scenario: **{label} air**.")

st.markdown("---")

st.markdown(
    "**Interpretation:** This simple model assumes trees absorb part of the "
    "pollution plume, electric buses cut tailpipe NO₂, and truck restrictions "
    "reduce heavy‑duty emissions. The exact numbers are illustrative, but the "
    "trend shows how combined actions can shift a micro‑zone from risky to safer."
)
with st.expander("How to read this scenario"):
    st.markdown(
        """
        - **New Breathability Index** shows where the air would land if this policy package is applied.
        - **Scenario Rating** compares the new index against the same Healthy / Caution / Unhealthy bands used in the Predictive Engine.
        - The NO₂ change is an approximate directional estimate, not a regulatory forecast.
        """
    )
