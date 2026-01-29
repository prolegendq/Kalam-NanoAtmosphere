import streamlit as st
from datetime import *
import numpy as np  # For demo metrics

st.set_page_config(page_title="KALAM NANOATMOSPHERE", layout="wide")

if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

# Log with CONSISTENT keys
st.session_state.user_logs.append({
    "user": st.session_state.get("user_email", "guest"),
    "action": "Page visited",
    "page": "Home",  # Change per page
    "timestamp": datetime.now().strftime("%H:%M:%S")
})
# ─── CLEAN TIGHT NAVBAR (no auth, moved up) ───
st.markdown("""
<style>
.navbar {
    background: linear-gradient(90deg, #0f0f23 0%, #1a1a3e 100%);
    padding: 6px 20px;  /* Reduced from 12px */
    border-bottom: 2px solid #00d4ff;
    box-shadow: 0 2px 8px rgba(0,212,255,0.3);  /* Tighter shadow */
    text-align: center;
    position: sticky;
    top: -2px;  /* Moved up slightly */
    z-index: 100;
    margin: -10px -20px 20px -20px;  /* Negative margins pull tighter */
}
.navbar a {
    color: #00d4ff;
    margin: 0 25px;
    font-weight: 600;
    font-size: 15px;
    text-decoration: none;
    padding: 8px 16px;
    border-radius: 20px;
    display: inline-block;
    transition: all 0.3s;
}
.navbar a:hover {
    color: white;
    background: rgba(0,212,255,0.2);
    text-shadow: 0 0 8px #00d4ff;
}
@media (max-width: 768px) {
    .navbar a { font-size: 13px; margin: 0 12px; padding: 6px 12px; }
}
</style>

<div class="navbar">
    <a href="#metrics">📊 Metrics</a>
    <a href="#overview">📈 Overview</a>
    <a href="#launch">🚀 Launch</a>
    <a href="#objectives">🎯 Objectives</a>
    <a href="#about">👨‍💻 About</a>
</div>
""", unsafe_allow_html=True)







# ─── TOP-RIGHT LOGIN/REGISTER BUTTONS ───
top_col1, top_col2, top_col3 = st.columns([8, 1, 1])

with top_col2:
    if not st.session_state.get("logged_in"):
        if st.button("Login", use_container_width=True):
            st.switch_page("pages/Login.py")
    else:
        st.write(f"👤 {st.session_state.get('user_email', '')[:10]}...")

with top_col3:
    if not st.session_state.get("logged_in"):
        if st.button("Register", use_container_width=True):
            st.switch_page("pages/Register.py")
    else:
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ─── CUSTOM SIDEBAR (only show main pages, not Login/Register) ───
with st.sidebar:
    st.markdown(
    """
    <h1 style='text-align: center;'>
        <span style='color: #F46DC3;'>Kalam </span><span style='color: #FBD85B;'>Nano</span><span style='color: #56D5F2;'>Atmosphere</span>
    </h1>
    """,
    unsafe_allow_html=True
)
    st.page_link("app.py", label="🏠 Home")

    if st.session_state.get("logged_in"):
        st.page_link("pages/1_God_Eye_National.py", label="🛰️ God-Eye National")
        st.page_link("pages/2_Predictive_Microclouds.py", label="☁️ Predictive Microclouds")
        st.page_link("pages/3_AI_Policy_Advisor.py", label="🤖 AI Policy Advisor")
        st.page_link("pages/4_WhatIf_Simulator.py", label="🔮WhatIf Simulator")
        st.page_link("pages/5_National_Reports.py", label="📄National Reports")
        st.page_link("pages/7_City_Intelligence.py", label=" 🌆City Intelligence")
        st.page_link("pages/8_Pollution_Alerts.py", label=" 📢Pollution Alerts")
        st.page_link("pages/9_Community_Hub.py", label=" 🌐Community Hub")
        st.page_link("pages/10_Traffic_intelligence.py", label="🚗Trafiic Intellligance")
        # Admin-only link
        if st.session_state.get("user_email") == "prolegendq7@gmail.com":
            st.page_link("pages/6_Admin_Panel.py", label="⚙️ Admin Panel")

# ─── MAIN CONTENT ───
st.markdown(
    """
    <h1 style='text-align: center;'>
        Welcome to <span style='color: #F46DC3;'>Kalam </span><span style='color: #FBD85B;'>Nano</span><span style='color: #56D5F2;'>Atmosphere</span>
    </h1>
    """,
    unsafe_allow_html=True
)
st.subheader("Autonomous Hyper-Local Pollution Intelligence System")

if not st.session_state.get("logged_in"):
    st.info("Please **Login** or **Register** (top-right) to access the dashboard.")
else:
    st.success(f"Logged in as {st.session_state.get('user_email')}")
# ─── KEY METRICS ROW (national overview) ───
st.markdown('<div id="metrics" class="section-anchor"></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

# Demo data (replace with real cached data later)
national_aqi = np.random.randint(80, 150)
hotspots_active = 127
cities_monitored = 45
alerts_today = np.random.randint(5, 15)

with col1:
    st.metric("🇮🇳 National AQI", f"{national_aqi}", delta="↑ 12%")
with col2:
    st.metric("🔴 Active Hotspots", hotspots_active, delta="-3")
with col3:
    st.metric("🏙️ Cities Covered", cities_monitored)
with col4:
    st.metric("🚨 Alerts Today", alerts_today, delta_color="inverse")

# ─── OVERVIEW CARDS ───
st.markdown('<div id="overview" class="section-anchor"></div>', unsafe_allow_html=True)
st.subheader("📈 Overview")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 At a Glance")
    st.markdown("""
    - **NO₂ Coverage**: 95% of urban India (Sentinel-5P)
    - **Prediction Horizon**: Next 24-72 hours breathability
    - **AI Advisor**: Policy recommendations for 50+ cities
    - **Data Freshness**: Updated every 6 hours
    """)

    st.info("**Status**: All systems nominal. Ready for city-level analysis.")

with col2:
    st.subheader("🎯 Quick Stats")
    st.markdown("""
    | Pollutant | National Avg | Trend |
    |-----------|--------------|--------|
    | NO₂      | 28 µg/m³    | 📈    |
    | SO₂      | 12 µg/m³    | 📉    |
    | CO       | 0.8 mg/m³   | ➡️    |
    | PM2.5    | 42 µg/m³    | 📈    |
    """)


st.markdown("---")
# ─── LAUNCH ───
st.markdown('<div id="launch" class="section-anchor"></div>', unsafe_allow_html=True)
st.subheader("🚀 Launch Analysis")
if st.button("🌐 Community Hub", use_container_width=True):
    st.switch_page("pages/9_Community_Hub.py")


st.markdown("---")
# ─── OBJECTIVES SECTION (single column, no split) ───
st.markdown('<div id="objectives" class="section-anchor"></div>', unsafe_allow_html=True)
st.subheader("🎯 Objectives")

st.markdown("""
**Primary Goals**  
• **Real-Time Monitoring**: Satellite NO₂ tracking for 45+ Indian cities (Sentinel-5P)  
• **Predictive Analytics**: 24-72hr breathability forecasts at hyper-local hotspots  
• **Actionable Intelligence**: AI policy briefs aligned with National Clean Air Programme (NCAP)  

**Measurable Impact**  
• Reduce pollution response time by **80%** for cities & schools  
• **Zero sensors** required—100% satellite + AI powered  
• Enable **data-driven green policies** nationwide  
• Scale to PM2.5, SO₂, CO in Phase 2 (Q2 2026)  

**Hackathon Target**  
**Top 1 placement** in National Hackathon 2026
""")

st.success("✅ **Built by Class 11 students**—proving AI can democratize environmental intelligence.")

st.markdown("---")
# ─── NEW: ABOUT US SECTION ───
# ─── ABOUT US (CARD STYLE, 2 CREATORS) ───
st.markdown('<div id="about"></div>', unsafe_allow_html=True)
st.header("👥 About the Creators")
# Global font tweaks just for this section
st.markdown("""
<style>
.about-name {
    font-size: 120px !important;      /* name bigger */
    font-weight: 700;
}
.about-title {
    font-size: 100px !important;      /* role label */
    letter-spacing: 1px;
}
.about-text {
    font-size: 100px !important;      /* description paragraph */
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

def creator_card(
    photo_path: str,
    name: str,
    title: str,
    paragraph: str,
    gmail_link: str = "#",
    insta_link: str = "#",
):
    with st.container(border=True):
        col_img, col_text = st.columns([1.2, 2])

        with col_img:
            st.image(photo_path, use_column_width=True)

        with col_text:
            st.markdown(f"### {name}")
            st.markdown(f"<span style='color:#0a8f5c; font-weight:600;'>{title}</span>",
                        unsafe_allow_html=True)
            st.write(paragraph)




# Creator 1
creator_card(
    photo_path="assets/creator1.jpg",  # put your image file here
    name="ANNAMALAI M",
    title="FOUNDER & HEAD OF ENGINEERING",
    paragraph=(
        "Annamalai M is an inspiring young developer whose curiosity and persistence drive every line of code he writes."
        "As a coding enthusiast, he dives deep into Python, UI frameworks, and app architecture, constantly experimenting with new ideas to make technology feel simple and powerful for everyday users."
        "He treats each project as a chance to learn something new—whether it is polishing the Nano Atmosphere interface, optimizing logic behind the scenes, or exploring AI-powered features that can turn raw data into clear, actionable insights for communities."
    ),


)

# Creator 2
creator_card(
    photo_path="assets/creator2.jpg",
    name="NL AADHITYA KUMAR",
    title="FOUNDER & TECHNICAL LEAD",
    paragraph=(
        "NL Aadhitya Kumar is the calm, strategic tech head who ensures that bold ideas become realistic, scalable systems rather than just concepts on paper."
         "With a strong focus on structure, reliability, and long-term vision, he leads decisions on architecture, feature priorities, and how different components of Nano Atmosphere and related projects fit together into a coherent whole."
        "His leadership combines technical depth with clear thinking, helping the team maintain a professional standard that matches serious real-world use, from community reporting tools to a startup-grade Nano Atmosphere platform."
    ),

)

# ─── FOOTER INFO ───
st.markdown("---")
st.caption("🛰️ Powered by Sentinel-5P • 🤖 AI Policy Engine • Updated Jan 2026")