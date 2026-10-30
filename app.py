import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Public Heat Stress Monitoring",
    page_icon="🌡️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #071426;
    color: white;
}
section[data-testid="stSidebar"] {
    background: #0c1c32;
}
.metric-card {
    background: #102641;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #203c5b;
}
.metric-title {
    color: #9bb2cc;
    font-size: 13px;
}
.metric-value {
    color: white;
    font-size: 30px;
    font-weight: bold;
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
st.sidebar.caption("ESP32 Monitoring System")

@st.cache_resource
def connect_database():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

try:
    supabase = connect_database()

    readings = supabase.table(
        "sensor_readings"
    ).select("*").order(
        "timestamp", desc=True
    ).limit(500).execute().data

    alerts = supabase.table(
        "alerts"
    ).select("*").order(
        "timestamp", desc=True
    ).limit(100).execute().data

    devices = supabase.table(
        "device_status"
    ).select("*").execute().data

except Exception as e:
    st.error("Database connection failed.")
    st.code(str(e))
    st.stop()

df = pd.DataFrame(readings)
alert_df = pd.DataFrame(alerts)
device_df = pd.DataFrame(devices)

if not df.empty:
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], utc=True
    ).dt.tz_convert("Asia/Kolkata")

    latest = df.iloc[0]
else:
    latest = {}

if not alert_df.empty:
    alert_df["timestamp"] = pd.to_datetime(
        alert_df["timestamp"], utc=True
    ).dt.tz_convert("Asia/Kolkata")

def display_metric(title, value, unit):
    if pd.isna(value) if value is not None else True:
        value = "--"
    else:
        value = f"{value:.1f}"

    st.markdown(
        f"""
        <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value} {unit}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def show_metrics():
    fields = [
        ("HEART RATE", "heart_rate", "BPM"),
        ("SpO₂", "spo2", "%"),
        ("TEMPERATURE", "temperature", "°C"),
        ("HUMIDITY", "humidity", "%"),
        ("PRESSURE", "pressure", "hPa"),
        ("HEAT INDEX", "heat_index", "°C")
    ]

    for start in (0, 3):
        cols = st.columns(3)
        for col, item in zip(cols, fields[start:start+3]):
            with col:
                display_metric(
                    item[0],
                    latest.get(item[1]),
                    item[2]
                )

def show_graphs():
    if df.empty:
        st.info("Waiting for sensor readings.")
        return

    graph_fields = {
        "Heart Rate": ("heart_rate", "BPM"),
        "SpO₂": ("spo2", "%"),
        "Temperature": ("temperature", "°C"),
        "Humidity": ("humidity", "%"),
        "Pressure": ("pressure", "hPa"),
        "Heat Index": ("heat_index", "°C")
    }

    for name, (field, unit) in graph_fields.items():
        if field in df.columns and df[field].notna().any():
            fig = px.line(
                df.sort_values("timestamp"),
                x="timestamp",
                y=field,
                title=name,
                markers=True,
                template="plotly_dark"
            )
            fig.update_layout(
                paper_bgcolor="#071426",
                plot_bgcolor="#0c1c32",
                yaxis_title=unit,
                xaxis_title="Time"
            )
            st.plotly_chart(fig, use_container_width=True)

st.title("Public Heat Stress Monitoring System")
st.caption("Real-Time Environmental & Physiological Monitoring")

if page == "Dashboard":
    show_metrics()

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.subheader("ML Risk Prediction")

        if latest:
            risk = latest.get("ml_risk") or "Not available"
            st.info(f"Current predicted risk: {risk}")
        else:
            st.info("Waiting for sensor data and ML model.")

    with right:
        st.subheader("System Status")

        if not device_df.empty:
            for _, device in device_df.iterrows():
                st.write("Device:", device["device_id"])
                st.write(
                    "Status:",
                    device["connection_status"]
                )
                st.write("Last seen:", device["last_seen"])
        else:
            st.warning("No device registered.")

    st.markdown("---")
    st.subheader("Environmental & Physiological Trends")
    show_graphs()

    st.markdown("---")
    st.subheader("Recent Alerts")

    if not alert_df.empty:
        st.dataframe(
            alert_df.head(5),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No alerts recorded.")

elif page == "Live Data":
    st.subheader("Latest Sensor Measurements")
    show_metrics()

    if latest:
        st.write("Last recorded:", latest["timestamp"])
    else:
        st.info("Waiting for ESP32 data.")

elif page == "Graphs & Analytics":
    st.subheader("Sensor Analytics")
    show_graphs()

elif page == "Alert History":
    st.subheader("Alert History")

    if not alert_df.empty:
        st.dataframe(
            alert_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No alert records available.")

elif page == "Data Records":
    st.subheader("Historical Sensor Records")

    if not df.empty:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No sensor records available.")

elif page == "ML Model":
    st.subheader("Machine Learning Analysis")
    st.info("The trained prediction model will be integrated in the next stage.")
    if latest:
        st.write("Latest recorded risk:", latest.get("ml_risk"))

elif page == "Device Status":
    st.subheader("ESP32 Device Status")

    if not device_df.empty:
        st.dataframe(
            device_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No ESP32 device connected yet.")

elif page == "Project Info":
    st.subheader("About the Project")

    st.write("""
    Public Heat Stress Monitoring and Alert System

    Hardware:
    - ESP32
    - MAX30102
    - Environmental sensor
    - OLED display
    - LED alert
    - Buzzer alert

    Software:
    - Python
    - Streamlit
    - Supabase
    - Plotly
    - Machine Learning

    Data recording interval: 2 minutes.
    """)

st.sidebar.markdown("---")
st.sidebar.write("Records:", len(df))
st.sidebar.write("Alerts:", len(alert_df))

if not df.empty:
    csv = df.to_csv(index=False).encode("utf-8")

    st.sidebar.download_button(
        "Download CSV",
        csv,
        "heat_stress_records.csv",
        "text/csv"
    )

st.sidebar.caption(
    "Last dashboard refresh: " +
    datetime.now(
        ZoneInfo("Asia/Kolkata")
    ).strftime("%d-%m-%Y %H:%M:%S")
)

if st.button("Refresh Dashboard"):
    st.rerun()