import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Public Heat Stress Monitoring System",
    page_icon="🌡️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #071426;
    color: white;
}
[data-testid="stSidebar"] {
    background-color: #102139;
}
.metric-card {
    background: #142943;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #263f5c;
    margin-bottom: 10px;
}
.metric-title {
    color: #a8b8cc;
    font-size: 14px;
}
.metric-value {
    color: white;
    font-size: 29px;
    font-weight: bold;
}
.metric-unit {
    color: #9baec5;
    font-size: 13px;
}
.status {
    padding: 7px 12px;
    border-radius: 8px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


def generate_demo_data():
    np.random.seed(42)

    now = datetime.now()
    times = [now - timedelta(minutes=2*i) for i in range(119, -1, -1)]

    temperature = np.random.normal(32.5, 1.3, 120)
    humidity = np.random.normal(60, 5, 120)
    pressure = np.random.normal(1010, 2, 120)
    heart_rate = np.random.normal(82, 8, 120)
    spo2 = np.random.normal(97, 1, 120)

    df = pd.DataFrame({
        "Timestamp": times,
        "Temperature": temperature,
        "Humidity": humidity,
        "Pressure": pressure,
        "Heart_Rate": heart_rate,
        "SpO2": spo2
    })

    df["Temperature"] = df["Temperature"].clip(20, 45)
    df["Humidity"] = df["Humidity"].clip(20, 95)
    df["Heart_Rate"] = df["Heart_Rate"].clip(45, 150)
    df["SpO2"] = df["SpO2"].clip(90, 100)

    df["Heat_Index"] = [
        calculate_heat_index(t, h)
        for t, h in zip(df["Temperature"], df["Humidity"])
    ]

    df["Heat_Risk"] = df["Heat_Index"].apply(heat_risk)
    df["Health_Risk"] = df["Heart_Rate"].apply(health_risk)

    return df


def calculate_heat_index(temp, humidity):
    tf = temp * 9/5 + 32

    hi = (
        -42.379
        + 2.04901523 * tf
        + 10.14333127 * humidity
        - 0.22475541 * tf * humidity
        - 0.00683783 * tf**2
        - 0.05481717 * humidity**2
        + 0.00122874 * tf**2 * humidity
        + 0.00085282 * tf * humidity**2
        - 0.00000199 * tf**2 * humidity**2
    )

    return (hi - 32) * 5/9


def heat_risk(value):
    if value >= 41:
        return "Very High"
    elif value >= 35:
        return "High"
    elif value >= 32:
        return "Moderate"
    return "Low"


def health_risk(value):
    if value > 100:
        return "High"
    return "Normal"


def metric(title, value, unit):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)


if "data" not in st.session_state:
    st.session_state.data = generate_demo_data()

if "source" not in st.session_state:
    st.session_state.source = "DEMO DATA"

df = st.session_state.data.copy()

with st.sidebar:
    st.markdown("## 🌡️ HEAT MONITOR")
    st.caption("PUBLIC HEALTH MONITORING")
    st.divider()

    page = st.radio(
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

    st.divider()

    st.markdown("### ESP32 Monitoring System")
    st.error("ESP32 Offline")
    st.caption("Hardware under inspection")
    st.caption("Data source: " + st.session_state.source)
    st.caption(f"Records: {len(df)}")

    st.divider()

    if st.button("Refresh Dashboard", use_container_width=True):
        if st.session_state.source == "DEMO DATA":
            st.session_state.data = generate_demo_data()
        st.rerun()

    uploaded = st.file_uploader(
        "Import historical CSV",
        type=["csv"]
    )

    if uploaded is not None:
        try:
            imported = pd.read_csv(uploaded)

            required = [
                "Temperature",
                "Humidity",
                "Pressure",
                "Heart_Rate"
            ]

            if all(c in imported.columns for c in required):
                if "Timestamp" not in imported.columns:
                    imported["Timestamp"] = pd.date_range(
                        end=datetime.now(),
                        periods=len(imported),
                        freq="2min"
                    )

                imported["Heat_Index"] = [
                    calculate_heat_index(t, h)
                    for t, h in zip(
                        imported["Temperature"],
                        imported["Humidity"]
                    )
                ]

                imported["Heat_Risk"] = imported["Heat_Index"].apply(heat_risk)
                imported["Health_Risk"] = imported["Heart_Rate"].apply(health_risk)

                st.session_state.data = imported
                st.session_state.source = "UPLOADED HISTORICAL DATA"
                st.rerun()

            else:
                st.error("CSV is missing required columns.")

        except Exception as e:
            st.error(str(e))


latest = df.iloc[-1]

st.title("🌡️ Public Heat Stress Monitoring System")
st.caption("Real-Time Environmental and Physiological Monitoring")

if st.session_state.source == "DEMO DATA":
    st.warning("DEMONSTRATION MODE — These are simulated readings, not live sensor measurements.")
elif st.session_state.source == "UPLOADED HISTORICAL DATA":
    st.info("HISTORICAL MODE — Displaying readings imported from your CSV file.")

st.markdown(
    f"**Last dashboard update:** {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
)

if page == "Dashboard":

    st.subheader("Environmental Monitoring")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric("Temperature", f"{latest['Temperature']:.1f}", "°C")

    with c2:
        metric("Humidity", f"{latest['Humidity']:.1f}", "%")

    with c3:
        metric("Atmospheric Pressure", f"{latest['Pressure']:.1f}", "hPa")

    st.subheader("Physiological Monitoring")

    c4, c5, c6 = st.columns(3)

    with c4:
        metric("Heart Rate", f"{latest['Heart_Rate']:.0f}", "BPM")

    with c5:
        spo2_value = latest["SpO2"] if "SpO2" in df.columns else np.nan
        metric("SpO2", f"{spo2_value:.1f}" if pd.notna(spo2_value) else "N/A", "%")

    with c6:
        metric("Heat Index", f"{latest['Heat_Index']:.1f}", "°C")

    st.subheader("Risk Analysis")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Heat Stress Risk")
        st.warning(str(latest["Heat_Risk"]))

    with c2:
        st.markdown("### Physiological Indicator")
        st.info(str(latest["Health_Risk"]))

    st.subheader("Recent Environmental Trends")

    fig = px.line(
        df.tail(30),
        x="Timestamp",
        y="Temperature",
        title="Temperature Trend",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Risk categories are illustrative project thresholds, not medical diagnoses.")

elif page == "Live Data":

    st.subheader("Live Monitoring Interface")

    st.info("The ESP32 is currently offline. The following values are demonstration readings.")

    st.dataframe(
        df.tail(20).sort_values("Timestamp", ascending=False),
        use_container_width=True,
        hide_index=True
    )

elif page == "Graphs & Analytics":

    st.subheader("Graphs and Analytics")

    variables = [
        "Temperature",
        "Humidity",
        "Pressure",
        "Heart_Rate",
        "SpO2",
        "Heat_Index"
    ]

    selected = st.selectbox("Select parameter", variables)

    fig = px.line(
        df,
        x="Timestamp",
        y=selected,
        title=f"{selected} History",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(
        df,
        x="Temperature",
        y="Humidity",
        color="Heat_Risk",
        title="Temperature vs Humidity",
        template="plotly_dark"
    )

    st.plotly_chart(fig2, use_container_width=True)

elif page == "Alert History":

    st.subheader("Alert History")

    alerts = df[
        (df["Heat_Risk"].isin(["High", "Very High"]))
        | (df["Health_Risk"] == "High")
    ].copy()

    if alerts.empty:
        st.success("No alert conditions in the displayed records.")
    else:
        st.dataframe(
            alerts[
                [
                    "Timestamp",
                    "Temperature",
                    "Heat_Index",
                    "Heart_Rate",
                    "Heat_Risk",
                    "Health_Risk"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    st.caption("Alerts are calculated from the displayed dataset.")

elif page == "Data Records":

    st.subheader("Complete Data Records")

    st.dataframe(
        df.sort_values("Timestamp", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        csv,
        "heat_stress_records.csv",
        "text/csv",
        use_container_width=True
    )

elif page == "ML Model":

    st.subheader("Machine Learning Module")

    st.warning("ML model training and validation have not been implemented. This section currently shows rule-based analysis.")

    st.markdown("""
    **Input Parameters**
    - Temperature
    - Humidity
    - Heat Index
    - Heart Rate

    **Current Analysis Method**

    Threshold-based risk classification.

    **Future Development**
    - Dataset preparation
    - Feature engineering
    - Model training
    - Model evaluation
    - Predictive risk classification
    """)

    st.write("Current Heat Risk:", latest["Heat_Risk"])
    st.write("Current Health Indicator:", latest["Health_Risk"])

elif page == "Device Status":

    st.subheader("Hardware Device Status")

    st.error("ESP32: OFFLINE")

    st.write("Microcontroller: ESP32 DevKit")
    st.write("Environmental Sensor: BME280")
    st.write("Physiological Sensor: MAX30102")
    st.write("Display: OLED 0.96 inch")
    st.write("Communication: Wi-Fi")
    st.write("Hardware condition: Under inspection")

    st.info("The dashboard remains available independently of the hardware.")

elif page == "Project Info":

    st.subheader("About the Project")

    st.markdown("""
    **Public Heat Stress Monitoring and Alert System**

    An ESP32-based prototype designed to monitor environmental
    and physiological indicators associated with heat stress.

    **Hardware Components**
    - ESP32 Microcontroller
    - BME280 Environmental Sensor
    - MAX30102 Optical Sensor
    - OLED Display
    - LED Indicator
    - Buzzer Alert

    **Software Technologies**
    - Python
    - Streamlit
    - Pandas
    - NumPy
    - Plotly
    - IoT Communication

    **Project Objectives**
    - Environmental data monitoring
    - Physiological parameter monitoring
    - Heat index calculation
    - Risk indication
    - Historical data visualization
    - Remote monitoring interface

    **Project Status**

    Dashboard demonstration available.
    Hardware currently under inspection.
    """)

st.divider()

st.caption(
    "Public Heat Stress Monitoring System | "
    "Educational Prototype | "
    "Demonstration and Historical Data Interface"
)