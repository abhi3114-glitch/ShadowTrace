import streamlit as st
import time
import threading
import pandas as pd
import plotly.express as px
from datetime import datetime
from sensors.simulated import SimulatedSensor
from database.db_manager import DBManager
from analysis.movement import MovementAnalyzer

# Page Config
st.set_page_config(
    page_title="ShadowTrace",
    page_icon="👣",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Premium" feel
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- Singleton Logger Class ---
class SensorLogger:
    def __init__(self):
        self.sensor = self._select_sensor()
        self.db = DBManager()
        self.running = False
        self.thread = None
        self.latest_reading = None
    
    def _select_sensor(self):
        # Try Loading Native
        try:
            from sensors.windows_native import WindowsNativeSensor
            sensor = WindowsNativeSensor()
            # We need to temporarily start it to check if hardware is present
            sensor.start()
            if sensor.accelerometer:
                sensor.stop() # Reset
                print("Using WindowsNativeSensor")
                return sensor
            else:
                sensor.stop()
                print("WindowsNativeSensor loaded but no hardware found. Falling back.")
        except ImportError:
            print("winsdk not installed. Falling back.")
        except Exception as e:
            print(f"Error loading native sensor: {e}")

        print("Using SimulatedSensor")
        return SimulatedSensor()

    def start(self):
        # Prevent multiple threads
        if self.running:
            return
        
        self.running = True
        self.sensor.start()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("SensorLogger started")

    def _loop(self):
        while self.running:
            reading = self.sensor.get_reading()
            if reading:
                self.latest_reading = reading
                # Log to DB
                self.db.log_reading(reading)
            # Sleep for 200ms (5Hz)
            time.sleep(0.2)
    
    def stop(self):
        self.running = False
        self.sensor.stop()
        if self.thread:
            self.thread.join()

# --- Cache the Logger so it survives re-runs ---
@st.cache_resource
def get_logger():
    logger = SensorLogger()
    logger.start()
    return logger

logger = get_logger()

# --- Sidebar ---
st.sidebar.title("ShadowTrace 👣")
st.sidebar.markdown("Laptop Movement Tracker")

if st.sidebar.button("Refresh Data"):
    st.rerun()

st.sidebar.markdown("---")
mode_text = "Real Sensors (Windows)" if "WindowsNativeSensor" in str(type(logger.sensor)) else "Simulation Mode"
st.sidebar.info(f"**Mode:** {mode_text}")

if "Simul" in mode_text:
    st.sidebar.caption("Using simulated data because no accelerometer was detected.")


# --- Main Dashboard ---
st.title("Today's Movement")

# Metrics Row
col1, col2, col3 = st.columns(3)

# Fetch Data
db = DBManager()
analyzer = MovementAnalyzer()
df = db.get_todays_logs()

# 1. Current Status
current_status = "Unknown"
acc_val = "0.00"
if logger.latest_reading:
    moving = logger.latest_reading.is_moving
    current_status = "Active 🏃" if moving else "Stationary 🧘"
    acc_val = f"{logger.latest_reading.acc_x:.2f}, {logger.latest_reading.acc_y:.2f}"

with col1:
    st.metric("Live Status", current_status, delta=acc_val, delta_color="off")

# 2. Total Movements
total_moves = 0
if not df.empty:
    total_moves = analyzer.calculate_daily_stat(df)
    # Approx seconds
    total_seconds = total_moves * 0.2 
    total_minutes = total_seconds / 60

with col2:
    st.metric("Active Time (Today)", f"{total_minutes:.1f} min", f"{total_moves} samples")

# 3. Light Level
light_val = 0
if logger.latest_reading:
    light_val = logger.latest_reading.light_level

with col3:
    st.metric("Ambient Light", f"{light_val:.0f} lux")

# --- Visualizations ---

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Hourly Activity")
    hourly_df = db.get_hourly_activity()
    if not hourly_df.empty:
        fig_bar = px.bar(
            hourly_df, 
            x='hour', 
            y='activity_count',
            labels={'hour': 'Hour of Day', 'activity_count': 'Movement Samples'},
            color='activity_count',
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No activity recorded yet today.")

with col_right:
    st.subheader("Movement Intensity (Heatmap)")
    # Since we don't have XY map, we use Scatter 3D or 2D of Accel Vectors as proxy for "Variety of positions"
    if not df.empty and len(df) > 10:
        # Sample for performance if needed
        plot_df = df.iloc[::2] 
        fig_scatter = px.scatter(
            plot_df,
            x='acc_x',
            y='acc_z',
            color='light_level',
            size='is_moving',
            size_max=10,
            opacity=0.6,
            title="Tilt Distribution (X vs Z)"
        )
        fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Waiting for more data points...")

# --- Raw Data Table ---
with st.expander("Raw Sensor Data"):
    st.dataframe(df)

# Export
if not df.empty:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='shadowtrace_logs.csv',
        mime='text/csv',
    )
