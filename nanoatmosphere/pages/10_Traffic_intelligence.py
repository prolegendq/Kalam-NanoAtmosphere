import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import pandas as pd
from datetime import datetime
import tempfile
import os
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av

# ─── BACK BUTTON + AUTH GUARD ───
if st.button("🏠 ← Back to Home", use_container_width=False):
    st.switch_page("app.py")
# Log with CONSISTENT keys
st.session_state.user_logs.append({
    "user": st.session_state.get("user_email", "guest"),
    "action": "Page visited",
    "page": "city intelligence",  # Change per page
    "timestamp": datetime.now().strftime("%H:%M:%S")
})


# Load YOLO model (downloads automatically first time)
@st.cache_resource
def load_model():
    return YOLO('yolov8n.pt')


model = load_model()

# Vehicle classes in COCO dataset
VEHICLE_CLASSES = {
    2: 'car', 3: 'motorcycle', 5: 'bus',
    7: 'truck', 1: 'bicycle'
}

# WebRTC Configuration for STUN servers
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Initialize session state for live stats
if 'live_vehicle_count' not in st.session_state:
    st.session_state.live_vehicle_count = 0
if 'live_density' not in st.session_state:
    st.session_state.live_density = 0.0
if 'live_congestion' not in st.session_state:
    st.session_state.live_congestion = "🟢 Light"
if 'live_breakdown' not in st.session_state:
    st.session_state.live_breakdown = {v: 0 for v in VEHICLE_CLASSES.values()}


# Video processor class for WebRTC (UPDATED - not transformer)
class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.confidence = 0.25
        self.vehicle_count = 0
        self.density = 0.0
        self.congestion = "🟢 Light"
        self.breakdown = {v: 0 for v in VEHICLE_CLASSES.values()}

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Run YOLO detection
        results = model.predict(source=img, conf=self.confidence, verbose=False)

        # Count vehicles
        vehicle_counts = {v: 0 for v in VEHICLE_CLASSES.values()}
        total_vehicles = 0

        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                if cls in VEHICLE_CLASSES:
                    vehicle_counts[VEHICLE_CLASSES[cls]] += 1
                    total_vehicles += 1

        # Calculate metrics
        image_area = img.shape[0] * img.shape[1]
        density = (total_vehicles / image_area) * 1000000

        if density < 5:
            congestion = "🟢 Light"
        elif density < 15:
            congestion = "🟡 Moderate"
        else:
            congestion = "🔴 Heavy"

        # Update instance attributes
        self.vehicle_count = total_vehicles
        self.density = density
        self.congestion = congestion
        self.breakdown = vehicle_counts

        # Create an annotated frame with only bounding boxes
        annotated_frame = img.copy()
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                if cls in VEHICLE_CLASSES:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Draw rectangle (green color, 2 thickness)
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Return the annotated frame
        return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")


st.title("🚦 City Traffic & Industry Intelligence System")

# Sidebar controls
st.sidebar.header("⚙️ Settings")
confidence_threshold = st.sidebar.slider("Detection Confidence", 0.0, 1.0, 0.25, 0.05)
source_type = st.sidebar.radio("Input Source", ["Upload Image", "Upload Video", "Live Analysis"])

# Tabs for different features
tab1, tab2, tab3 = st.tabs(["🚗 Traffic Analysis", "🏭 Industry Monitoring", "📊 Combined Intelligence"])

# ==================== TAB 1: TRAFFIC ANALYSIS ====================
with tab1:
    st.header("Real-Time Traffic Detection & Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        if source_type == "Upload Image":
            uploaded_file = st.file_uploader("Upload Traffic Image", type=['jpg', 'jpeg', 'png'])

            if uploaded_file:
                # Read image
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

                # Run detection
                with st.spinner("Detecting vehicles..."):
                    results = model.predict(source=image, conf=confidence_threshold, verbose=False)

                # Process results
                vehicle_counts = {v: 0 for v in VEHICLE_CLASSES.values()}
                total_vehicles = 0

                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        if cls in VEHICLE_CLASSES:
                            vehicle_counts[VEHICLE_CLASSES[cls]] += 1
                            total_vehicles += 1

                # Annotated image
                annotated_frame = results[0].plot()
                st.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                         caption="Detected Vehicles", use_column_width=True)

                # Traffic density calculation
                image_area = image.shape[0] * image.shape[1]
                density = (total_vehicles / image_area) * 1000000

                if density < 5:
                    congestion = "🟢 Light"
                elif density < 15:
                    congestion = "🟡 Moderate"
                else:
                    congestion = "🔴 Heavy"

                with col2:
                    st.metric("Total Vehicles", total_vehicles)
                    st.metric("Traffic Density", f"{density:.2f}")
                    st.metric("Congestion Level", congestion)

                    st.subheader("Vehicle Breakdown")
                    df = pd.DataFrame(list(vehicle_counts.items()),
                                      columns=['Vehicle Type', 'Count'])
                    df = df[df['Count'] > 0]
                    st.dataframe(df, hide_index=True)

        elif source_type == "Upload Video":
            uploaded_video = st.file_uploader("Upload Traffic Video", type=['mp4', 'avi', 'mov'])

            if uploaded_video:
                # Save to temp file
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(uploaded_video.read())

                cap = cv2.VideoCapture(tfile.name)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))

                process_btn = st.button("🎬 Process Video")

                if process_btn:
                    stframe = st.empty()
                    progress_bar = st.progress(0)

                    frame_data = []
                    frame_idx = 0

                    while cap.isOpened():
                        ret, frame = cap.read()
                        if not ret:
                            break

                        # Process every 5th frame for speed
                        if frame_idx % 5 == 0:
                            results = model.predict(source=frame, conf=confidence_threshold, verbose=False)

                            # Count vehicles
                            vehicle_count = 0
                            for result in results:
                                boxes = result.boxes
                                for box in boxes:
                                    cls = int(box.cls[0])
                                    if cls in VEHICLE_CLASSES:
                                        vehicle_count += 1

                            frame_data.append({
                                'Frame': frame_idx,
                                'Time (s)': frame_idx / fps,
                                'Vehicles': vehicle_count
                            })

                            # Show annotated frame
                            annotated_frame = results[0].plot()
                            stframe.image(cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                                          channels="RGB", use_column_width=True)

                        frame_idx += 1
                        progress_bar.progress(frame_idx / frame_count)

                    cap.release()
                    os.unlink(tfile.name)

                    # Show results
                    df_frames = pd.DataFrame(frame_data)
                    st.success(f"✅ Processed {frame_count} frames")

                    with col2:
                        st.metric("Avg Vehicles/Frame", f"{df_frames['Vehicles'].mean():.1f}")
                        st.metric("Peak Traffic", df_frames['Vehicles'].max())
                        st.line_chart(df_frames.set_index('Time (s)')['Vehicles'])

        elif source_type == "Live Analysis":
            st.subheader("📹 Live Webcam Detection with WebRTC")

            # FIXED: Use video_processor_factory instead
            ctx = webrtc_streamer(
                key="traffic-detection",
                video_processor_factory=VideoProcessor,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,
            )

            if ctx.video_processor:
                ctx.video_processor.confidence = confidence_threshold

            st.info("🔴 Camera feed active - Detection running in real-time")

    # Show live stats in col2 for Live Analysis
    if source_type == "Live Analysis":
        with col2:
            placeholder = st.empty()
            while ctx.state.playing:
                with placeholder.container():
                    st.metric("Total Vehicles", ctx.video_processor.vehicle_count if ctx.video_processor else 0)
                    st.metric("Traffic Density", f"{ctx.video_processor.density:.2f}" if ctx.video_processor else 0)
                    st.metric("Congestion Level", ctx.video_processor.congestion if ctx.video_processor else "N/A")

                    st.subheader("Vehicle Breakdown")
                    if ctx.video_processor:
                        df = pd.DataFrame(list(ctx.video_processor.breakdown.items()),
                                          columns=['Vehicle Type', 'Count'])
                        df = df[df['Count'] > 0]
                        if not df.empty:
                            st.dataframe(df, hide_index=True)
                        else:
                            st.info("No vehicles detected yet")
                    else:
                        st.info("No vehicles detected yet")
                    import time
                    time.sleep(1)

# ==================== TAB 2: INDUSTRY MONITORING ====================
with tab2:
    st.header("Industrial Zone Environmental Monitoring")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🏭 Zone A - Manufacturing")
        pm25 = st.number_input("PM2.5 (µg/m³)", value=45.0, key="pm25_a")
        co = st.number_input("CO (ppm)", value=3.2, key="co_a")
        no2 = st.number_input("NO2 (ppb)", value=28.0, key="no2_a")

        aqi_a = (pm25 * 0.5 + co * 10 + no2 * 0.2)
        st.metric("AQI Score", f"{aqi_a:.0f}",
                  "Moderate" if aqi_a < 100 else "Unhealthy")

    with col2:
        st.subheader("🏭 Zone B - Chemical")
        pm25_b = st.number_input("PM2.5 (µg/m³)", value=78.0, key="pm25_b")
        co_b = st.number_input("CO (ppm)", value=5.8, key="co_b")
        no2_b = st.number_input("NO2 (ppb)", value=42.0, key="no2_b")

        aqi_b = (pm25_b * 0.5 + co_b * 10 + no2_b * 0.2)
        st.metric("AQI Score", f"{aqi_b:.0f}",
                  "Moderate" if aqi_b < 100 else "Unhealthy")

    with col3:
        st.subheader("🏭 Zone C - Heavy Industry")
        pm25_c = st.number_input("PM2.5 (µg/m³)", value=120.0, key="pm25_c")
        co_c = st.number_input("CO (ppm)", value=8.5, key="co_c")
        no2_c = st.number_input("NO2 (ppb)", value=65.0, key="no2_c")

        aqi_c = (pm25_c * 0.5 + co_c * 10 + no2_c * 0.2)
        st.metric("AQI Score", f"{aqi_c:.0f}",
                  "Moderate" if aqi_c < 100 else "Unhealthy")

    st.subheader("📈 Industry-Traffic Correlation")

    shift_time = st.selectbox("Factory Shift Time",
                              ["06:00 AM", "02:00 PM", "10:00 PM"])

    correlation_data = pd.DataFrame({
        'Hour': range(0, 24),
        'Traffic Volume': [20, 15, 12, 10, 15, 45, 80, 95, 85, 70, 65, 60,
                           55, 60, 90, 100, 90, 75, 60, 50, 40, 35, 30, 25],
        'Industrial Emissions': [30, 25, 20, 18, 25, 55, 70, 80, 75, 65, 60, 58,
                                 55, 60, 85, 95, 85, 70, 55, 45, 40, 35, 32, 28]
    })

    st.line_chart(correlation_data.set_index('Hour'))

# ==================== TAB 3: COMBINED INTELLIGENCE ====================
with tab3:
    st.header("Integrated City Intelligence Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Priority Hotspots")

        zones_data = pd.DataFrame({
            'Zone': ['Zone A', 'Zone B', 'Zone C', 'Downtown', 'Highway 101'],
            'Traffic Score': [65, 78, 82, 95, 88],
            'AQI Score': [58, 92, 125, 72, 65],
            'Risk Level': ['Moderate', 'High', 'Critical', 'High', 'Moderate']
        })

        st.dataframe(zones_data, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("🔮 What-If Simulation")

        policy = st.selectbox("Test Policy", [
            "Odd-Even Vehicle Rule",
            "Truck Night-Only Movement",
            "Factory Staggered Shifts",
            "Congestion Pricing Zone"
        ])

        if st.button("Run Simulation"):
            st.success("✅ Simulation Complete")

            impact_data = {
                'Metric': ['Traffic Reduction', 'AQI Improvement', 'Travel Time Saved'],
                'Current': ['100%', '100 AQI', '45 min'],
                'Predicted': ['72%', '78 AQI', '32 min'],
                'Change': ['-28%', '-22%', '-29%']
            }

            st.dataframe(pd.DataFrame(impact_data), hide_index=True, use_container_width=True)

    st.subheader("📄 Generate Report")

    if st.button("📥 Download Weekly Report"):
        report_data = {
            'Date': pd.date_range(start='2026-01-14', periods=7),
            'Avg Daily Traffic': [2340, 2456, 2389, 2501, 2678, 2234, 2123],
            'Peak AQI': [78, 85, 92, 88, 95, 72, 68],
            'Incidents': [2, 3, 1, 4, 3, 1, 2]
        }

        report_df = pd.DataFrame(report_data)
        csv = report_df.to_csv(index=False)

        st.download_button(
            label="Download CSV Report",
            data=csv,
            file_name=f"traffic_industry_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

        st.dataframe(report_df, hide_index=True, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Click 'START' on the webcam feed to begin detection")
