import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(
    page_title="Public Heat Stress Monitoring",
    page_icon="🌡️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #071426;
    color: #ffffff;
}
section[data-testid="stSidebar"] {
    background: #0c1c32;
}
.metric-card {
    background: #102641;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #203c5b;
    margin-bottom: 12px;
}
.metric-title {
    color: #9bb2cc;
    font-size: 14px;
}
.metric-value {
    color: white;
    font-size: 30px;
    font-weight: bold;
}
.metric-status {
    color: #36d6a0;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🌡️ HEAT MONITOR")
st.sidebar.caption("PUBLIC HEALTH MONITORING")
page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Dashboard",
        "Live Data",
        "Graphs & Analytics",
        "Alert History",
        "Data Records",
        "ML Model",
        "Device Status",
        "Project Info"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("🟢 System Interface")
st.sidebar.caption("ESP32 monitoring system")

st.title("Public Heat Stress Monitoring System")
st.caption("Real-Time Environmental & Physiological Monitoring")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="metric-card"><div class="metric-title">HEART RATE</div><div class="metric-value">-- BPM</div><div class="metric-status">Waiting for ESP32</div></div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="metric-card"><div class="metric-title">SpO₂</div><div class="metric-value">-- %</div><div class="metric-status">Waiting for sensor</div></div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="metric-card"><div class="metric-title">TEMPERATURE</div><div class="metric-value">-- °C</div><div class="metric-status">Waiting for sensor</div></div>', unsafe_allow_html=True)

c4, c5, c6 = st.columns(3)

with c4:
    st.markdown('<div class="metric-card"><div class="metric-title">HUMIDITY</div><div class="metric-value">-- %</div><div class="metric-status">Waiting for sensor</div></div>', unsafe_allow_html=True)

with c5:
    st.markdown('<div class="metric-card"><div class="metric-title">PRESSURE</div><div class="metric-value">-- hPa</div><div class="metric-status">Waiting for sensor</div></div>', unsafe_allow_html=True)

with c6:
    st.markdown('<div class="metric-card"><div class="metric-title">HEAT INDEX</div><div class="metric-value">-- °C</div><div class="metric-status">Waiting for sensor</div></div>', unsafe_allow_html=True)

st.markdown("---")

left, right = st.columns(2)

with left:
    st.subheader("ML Risk Prediction")
    st.info("Machine learning model not connected yet.")
    st.progress(0)

with right:
    st.subheader("System Status")
    st.warning("ESP32 connection pending")
    st.write("Database: Not connected")
    st.write("Last update: Awaiting data")

st.markdown("---")
st.subheader("Environmental & Physiological Trends")

times = pd.date_range(
    end=datetime.now(),
    periods=20,
    freq="2min"
)

demo = pd.DataFrame({
    "Time": times,
    "Heart Rate": np.zeros(20),
    "Temperature": np.zeros(20),
    "Humidity": np.zeros(20),
    "SpO2": np.zeros(20)
})

metric = st.selectbox(
    "Select parameter",
    ["Heart Rate", "Temperature", "Humidity", "SpO2"]
)

fig = px.line(
    demo,
    x="Time",
    y=metric,
    template="plotly_dark",
    markers=True
)

fig.update_layout(
    paper_bgcolor="#071426",
    plot_bgcolor="#0c1c32"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Recent Alerts")

st.info("No alert records available yet.")

st.caption("Public Heat Stress Monitoring System | ESP32 + IoT + Machine Learning")