import streamlit as st
from datetime import datetime
import pandas as pd
import uuid
import os
import pydeck as pdk

# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")


# Require login
if not st.session_state.get("logged_in"):
    st.error("🔒 Please log in to use the Community Reporting Hub.")
    st.stop()

USER_EMAIL = st.session_state.get("user_email", "anonymous")
ADMIN_EMAIL = "prolegendq7@gmail.com"

# ─── FILE PATHS FOR PERSISTENCE ───
DATA_PATH = "data"
REPORTS_CSV = os.path.join(DATA_PATH, "community_reports.csv")
SCORES_CSV = os.path.join(DATA_PATH, "user_scores.csv")
os.makedirs(DATA_PATH, exist_ok=True)

# ─── LOAD PERSISTENT STATE ───
def load_reports():
    if os.path.exists(REPORTS_CSV):
        df = pd.read_csv(REPORTS_CSV)
        # Convert lat and lon to numeric, coercing errors
        df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
        df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
        return df.to_dict("records")
    return []

def load_scores():
    if os.path.exists(SCORES_CSV):
        df = pd.read_csv(SCORES_CSV)
        return dict(zip(df["email"], df["points"]))
    return {}

if "community_reports" not in st.session_state:
    st.session_state.community_reports = load_reports()

if "user_scores" not in st.session_state:
    st.session_state.user_scores = load_scores()

# ─── SAVE HELPERS ───
def save_reports():
    df = pd.DataFrame(st.session_state.community_reports)
    df.to_csv(REPORTS_CSV, index=False)

def save_scores():
    df = pd.DataFrame(
        [{"email": e, "points": p} for e, p in st.session_state.user_scores.items()]
    )
    df.to_csv(SCORES_CSV, index=False)

# ─── UTILS ───
def add_points(email: str, points: int):
    if email not in st.session_state.user_scores:
        st.session_state.user_scores[email] = 0
    st.session_state.user_scores[email] += points
    save_scores()

def auto_validate_report(report: dict) -> bool:
    """
    Placeholder validation.
    Later: replace with real NO2 + MQ135 checks.
    If report location matches NO2 spike / sensor data -> True.
    """
    try:
        lat = float(report.get("lat", 0))
        lon = float(report.get("lon", 0))
    except (ValueError, TypeError):
        return False

    # Example dummy hotspot around Delhi
    if 28.4 <= lat <= 28.8 and 76.9 <= lon <= 77.4:
        return True
    return False

def get_reports_df() -> pd.DataFrame:
    if not st.session_state.community_reports:
        return pd.DataFrame(
            columns=[
                "id", "public_name", "category", "severity", "city",
                "lat", "lon", "description", "timestamp", "status", "auto_verified"
            ]
        )
    df = pd.DataFrame(st.session_state.community_reports)
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    return df


# ─── PAGE HEADER ───
st.title("🌐 Community Reporting Hub")
st.markdown(
    "**Crowdsourced pollution incident reporting, verification, and community impact tracking.**"
)

tab_report, tab_map, tab_resolved, tab_admin, tab_leaderboard = st.tabs(
    ["📤 Submit Report", "🗺️ Community Heatmap", "✅ Resolved Incidents", "🛡️ Admin Moderation", "🏅 Leaderboard"]
)

# ╔══════════════════════════════════╗
# ║ 1) REPORT SUBMISSION             ║
# ╚══════════════════════════════════╝
with tab_report:
    st.subheader("📤 Submit a Pollution Incident")

    with st.form("report_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(
                "Category",
                [
                    "Smoke",
                    "Traffic",
                    "Construction Dust",
                    "Odor",
                    "Factory Emissions",
                    "Other",
                ],
            )
            severity = st.slider(
                "Severity (1 = mild, 5 = extreme)", min_value=1, max_value=5, value=3
            )
            city = st.text_input(
                "City / Area", placeholder="Eg. New Delhi - Rohini Sector 13"
            )

        with col2:
            lat = st.number_input(
                "Latitude", value=0.0, format="%.6f",
                help="Use GPS/map for exact coordinates."
            )
            lon = st.number_input(
                "Longitude", value=0.0, format="%.6f",
                help="Use GPS/map for exact coordinates."
            )

        description = st.text_area(
            "Describe what you observed (what, when, where, impact)", height=120
        )

        photo = st.file_uploader(
            "Upload a photo (optional)", type=["jpg", "jpeg", "png"]
        )

        allow_public_name = st.checkbox(
            "Show my email/name publicly on this report", value=False
        )

        submitted = st.form_submit_button("Submit Incident 🚀")

    if submitted:
        report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # photo_path removed as per user request
        
        report = {
            "id": report_id,
            "user": USER_EMAIL,
            "public_name": USER_EMAIL if allow_public_name else "Anonymous",
            "category": category,
            "severity": severity,
            "city": city,
            "lat": float(lat),
            "lon": float(lon),
            "description": description,
            "timestamp": timestamp,
            "status": "Under Review",  # default
            "auto_verified": False,
            "has_photo": bool(photo), # Still record if photo was attached, just not saved
        }

        st.session_state.community_reports.append(report)

        # Gamification: base + severity
        add_points(USER_EMAIL, 5 + severity)

        # Auto-validate with placeholder logic
        if auto_validate_report(report):
            report["status"] = "Action Taken"
            report["auto_verified"] = True
            add_points(USER_EMAIL, 10)  # bonus

        save_reports()

        st.success(f"✅ Report {report_id} submitted! Thank you for contributing.")
        st.rerun()

# ╔══════════════════════════════════╗
# ║ 2) COMMUNITY HEATMAP + FEED      ║
# ╚══════════════════════════════════╝
with tab_map:
    st.subheader("🗺️ Community Incident Heatmap")

    df = get_reports_df()
    if df.empty:
        st.info("No reports yet. Be the first to submit a pollution incident!")
    else:
        # Basic map; can be upgraded to folium heatmap later
        try:
            map_df = df.dropna(subset=['lat', 'lon'])
            map_df = map_df.astype({"lat": float, "lon": float})
            
            # Define colors for different statuses
            map_df['color'] = map_df['status'].apply(lambda x: [0, 255, 0, 160] if x == 'Resolved' else [255, 0, 0, 160])

            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=pdk.ViewState(
                    latitude=map_df['lat'].mean(),
                    longitude=map_df['lon'].mean(),
                    zoom=5,
                    pitch=50,
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=map_df,
                        get_position='[lon, lat]',
                        get_color='color',
                        get_radius=1000,
                    ),
                ],
            ))
        except Exception as e:
            st.error(f"Error displaying map: {e}")
            st.warning(
                "Some reports have invalid coordinates; map shows only valid ones."
            )
            valid = df.dropna(subset=['lat', 'lon'])
            if not valid.empty:
                st.map(valid[["lat", "lon"]].astype(float), zoom=5, size=40)

        st.markdown("### 📋 Recent Reports")
        st.dataframe(
            df[
                [
                    "id",
                    "public_name",
                    "category",
                    "severity",
                    "city",
                    "status",
                    "auto_verified",
                    "timestamp",
                ]
            ].sort_values("timestamp", ascending=False),
            use_container_width=True,
        )

# ╔══════════════════════════════════╗
# ║ 2.5) RESOLVED INCIDENTS          ║
# ╚══════════════════════════════════╝
with tab_resolved:
    st.subheader("✅ Resolved Incidents")
    
    df = get_reports_df()
    resolved_df = df[df["status"] == "Resolved"]
    
    if resolved_df.empty:
        st.info("No resolved incidents yet.")
    else:
        st.dataframe(
            resolved_df[
                [
                    "id",
                    "public_name",
                    "category",
                    "severity",
                    "city",
                    "status",
                    "timestamp",
                ]
            ].sort_values("timestamp", ascending=False),
            use_container_width=True,
        )

# ╔══════════════════════════════════╗
# ║ 3) ADMIN MODERATION PANEL        ║
# ╚══════════════════════════════════╝
with tab_admin:
    st.subheader("🛡️ Admin Moderation Panel")

    if USER_EMAIL != ADMIN_EMAIL:
        st.error("Only the central admin can access this panel.")
    else:
        df = get_reports_df()
        if df.empty:
            st.info("No reports available to moderate yet.")
        else:
            col_top_left, col_top_right = st.columns([2, 1])

            with col_top_left:
                selected_id = st.selectbox(
                    "Select a report to review", options=df["id"].tolist()
                )

            report = next(
                (r for r in st.session_state.community_reports if r["id"] == selected_id), None
            )

            if report:
                st.markdown("---")
                st.markdown(f"**Report ID:** `{report['id']}`")
                st.markdown(
                    f"**Reporter:** {report['public_name']}  \n"
                    f"**Category:** {report['category']} | **Severity:** {report['severity']}"
                )
                st.markdown(
                    f"**Location:** {report['city']}  \n"
                    f"**Coordinates:** {report['lat']}, {report['lon']}"
                )
                st.markdown(
                    f"**Status:** `{report['status']}`  |  "
                    f"**Auto-verified:** `{report['auto_verified']}`"
                )
                st.write("**Description:**")
                st.write(report["description"] or "_No description provided._")

                st.markdown("### Moderation Actions")
                a1, a2, a3, a4 = st.columns(4)

                changed = False
                if a1.button("✅ Mark Action Taken", key=f"action_{report['id']}"):
                    report["status"] = "Action Taken"
                    changed = True
                if a2.button("🕒 Keep Under Review", key=f"review_{report['id']}"):
                    report["status"] = "Under Review"
                    changed = True
                if a3.button("✅ Mark Resolved", key=f"resolved_{report['id']}"):
                    report["status"] = "Resolved"
                    changed = True
                if a4.button("🚩 Reject Report", key=f"reject_{report['id']}"):
                    report["status"] = "Rejected"
                    changed = True

                if changed:
                    # Write back updated report
                    for i, r in enumerate(st.session_state.community_reports):
                        if r["id"] == report["id"]:
                            st.session_state.community_reports[i] = report
                            break
                    save_reports()
                    st.success(f"✅ Status updated to: {report['status']}")
                    st.rerun()

            st.markdown("### Impact Tracker")
            st.info(
                "Use the status field to move reports through: "
                "**Under Review → Action Taken → Resolved**. "
                "This shows clear impact to the community."
            )

# ╔══════════════════════════════════╗
# ║ 4) LEADERBOARD + BADGES          ║
# ╚══════════════════════════════════╝
with tab_leaderboard:
    st.subheader("🏅 Community Leaderboard")

    if not st.session_state.user_scores:
        st.info("No contributions yet. Reports will start populating the leaderboard.")
    else:
        scores = sorted(
            st.session_state.user_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        rows = []
        for rank, (email, points) in enumerate(scores, start=1):
            if points >= 100:
                badge = "🌟 Legend (100+ pts)"
            elif points >= 50:
                badge = "🔥 Pro (50+ pts)"
            elif points >= 20:
                badge = "✅ Trusted (20+ pts)"
            else:
                badge = "🆕 New"

            rows.append(
                {
                    "Rank": rank,
                    "User": email,
                    "Points": points,
                    "Badge": badge,
                }
            )

        st.table(pd.DataFrame(rows))
        st.caption(
            "🎮 Gamification: +5 base pts per report + severity bonus, "
            "+10 if auto-verified (matches NO₂/sensor). Monthly top contributor can be highlighted."
        )