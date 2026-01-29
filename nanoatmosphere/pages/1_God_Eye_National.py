import streamlit as st
import folium
from datetime import datetime
from streamlit_folium import st_folium
import rasterio
import numpy as np

if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

# Log with CONSISTENT keys
st.session_state.user_logs.append({
    "user": st.session_state.get("user_email", "guest"),
    "action": "Page visited",
    "page": "God eye",  # Change per page
    "timestamp": datetime.now().strftime("%H:%M:%S")
})
# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")
# 1) Load NO2 raster you exported from GEE
@st.cache_resource
def load_no2():
    src = rasterio.open("nanoatmosphere/data/NO2_Chennai.tif")
    arr = src.read(1)
    bounds = src.bounds
    return src, arr, bounds

src, arr, bounds = load_no2()

# 2) Build base map
center = [(bounds.top + bounds.bottom)/2, (bounds.left + bounds.right)/2]
m = folium.Map(location=center, zoom_start=11, tiles="CartoDB dark_matter")

# 3) Add heat layer (simple normalization)
arr_norm = (arr - np.nanmin(arr)) / (np.nanmax(arr) - np.nanmin(arr))
# You can convert this into points for HeatMap later; for demo, just show a bounds rectangle

folium.Rectangle(
    bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
    color="#ff0000",
    fill=True,
    fill_opacity=0.2,
).add_to(m)

# 4) Render + capture click
st.write("Click on the map to probe a micro-cloud.")
result = st_folium(m, width=1100, height=600)

clicked_lat, clicked_lon = None, None
if result and result.get("last_clicked"):
    clicked_lat = result["last_clicked"]["lat"]
    clicked_lon = result["last_clicked"]["lng"]
    st.session_state["clicked_point"] = (clicked_lat, clicked_lon)
    st.success(f"Selected point: {clicked_lat:.4f}, {clicked_lon:.4f}")
st.info(
    "Next: Open **Predictive Micro‑Cloud Engine** to see Breathability and Risk "
    "for this tile, then go to **AI Policy Advisor** to generate a policy plan."
)
