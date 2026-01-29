import streamlit as st
from datetime import datetime
import pandas as pd

ADMIN_EMAIL = "prolegendq7@gmail.com"
# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")
if not st.session_state.get("logged_in"):
    st.error("You must log in to access Kalam NanoAtmosphere.")
    st.stop()

if st.session_state.get("user_email") != ADMIN_EMAIL:
    st.error("You do not have permission to view the Admin Panel.")
    st.stop()




st.title('ADMIN PANEL')

# Initialize logs safely
if "user_logs" not in st.session_state:
    st.session_state.user_logs = []

st.markdown("# ⚙️ AETHERIS Admin")
st.markdown("**Control Center**")

# Safe metrics (unchanged)
total_logs = len(st.session_state.user_logs)
unique_users = len({log.get("user", "unknown") for log in st.session_state.user_logs})

col1, col2, col3 = st.columns(3)
with col1: st.metric("📝 Total Logs", total_logs)
with col2: st.metric("👥 Unique Users", unique_users)
with col3:
    if st.session_state.user_logs:
        last_time = st.session_state.user_logs[-1].get("timestamp", "N/A")
        st.metric("🕐 Last Activity", last_time)
    else:
        st.metric("🕐 Last Activity", "No logs")

st.markdown("---")

# FIXED USER LOGS TABLE + CSV EXPORT
st.subheader("👥 User Activity")
if st.session_state.user_logs:
    # Filter & format safe logs
    safe_logs = []
    for log in st.session_state.user_logs[-20:]:  # Last 20
        safe_logs.append({
            "user": log.get("user", "unknown"),
            "action": log.get("action", "unknown"),
            "page": log.get("page", "unknown"),
            "timestamp": log.get("timestamp", "N/A")
        })

    # Display table
    st.dataframe(
        safe_logs,
        use_container_width=True,
        column_config={
            "user": "User",
            "action": "Action",
            "page": "Page",
            "timestamp": "Time"
        },
        hide_index=True
    )

    # Buttons
    col1, col2 = st.columns(2)
    if col1.button("🗑️ Clear Logs"):
        st.session_state.user_logs.clear()
        st.success("✅ Logs cleared!")
        st.rerun()

    # FIXED CSV EXPORT
    if col2.button("📥 Export CSV"):
        df = pd.DataFrame(st.session_state.user_logs)
        csv = df.to_csv(index=False)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"aetheris_user_logs_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    st.info("📭 No activity yet")

st.subheader("🔧 Controls")
st.columns(3)[0].toggle("🤖 AI", key="ai")
st.caption("🔐 prolegendq7@gmail.com")
