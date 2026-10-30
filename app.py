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
    background: #071426;
    color: white;
}
[data-testid="stSidebar"] {
    background: #102139;
}
.metric-card {
    background: #142943;
    padding: 20px;
    border-radius: 13px;
    border: 1px solid #263f5c;
    min-height: 115px;
}
.metric-title {
    color: #a8b8cc;
    font-size: 14px;
}
.metric-value {
    color: white;
    font-size: 30px;
    font-weight: bold;
}
.metric-unit {
    color: #9baec5;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


def calculate_heat_index(temp, humidity):
    tf = temp * 9 / 5 + 32

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

    return (hi - 32) * 5 / 9


def heat_risk(value):
    if value >= 41:
        return "Very High"
    elif value >= 35:
        return "High"
    elif value >= 32:
        return "Moderate"
    return "Low"


def health_risk(value):
    if pd.isna(value):
        return "Unavailable"
    if value > 100:
        return "Elevated"
    return "Normal"


def prepare_data(df):
    df = df.copy()

    required = [
        "Temperature",
        "Humidity",
        "Pressure",
        "Heart_Rate"
    ]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    if "Timestamp" not in df.columns:
        df["Timestamp"] = pd.date_range(
            end=datetime.now(),
            periods=len(df),
            freq="2min"
        )
    else:
        df["Timestamp"] = pd.to_datetime(
            df["Timestamp"], errors="coerce"
        )

    if "SpO2" not in df.columns:
        df["SpO2"] = np.nan

    for col in ["Temperature", "Humidity", "Pressure",
                "Heart_Rate", "SpO2"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Heat_Index"] = [
        calculate_heat_index(t, h)
        if pd.notna(t) and pd.notna(h) else np.nan
        for t, h in zip(df["Temperature"], df["Humidity"])
    ]

    df["Heat_Risk"] = df["Heat_Index"].apply(
        lambda x: heat_risk(x) if pd.notna(x) else "Unavailable"
    )

    df["Health_Risk"] = df["Heart_Rate"].apply(health_risk)

    return df


def metric(title, value, unit):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)


def create_dataset():
    np.random.seed(42)

    times = [
        datetime.now() - timedelta(minutes=2*i)
        for i in range(119, -1, -1)
    ]

    df = pd.DataFrame({
        "Timestamp": times,
        "Temperature": np.random.normal(32.5, 1.3, 120),
        "Humidity": np.random.normal(60, 5, 120),
        "Pressure": np.random.normal(1010, 2, 120),
        "Heart_Rate": np.random.normal(82, 8, 120),
        "SpO2": np.random.normal(97, 1, 120)
    })

    return prepare_data(df)


if "data" not in st.session_state:
    st.session_state.data = create_dataset()

if "data_source" not in st.session_state:
    st.session_state.data_source = "Monitoring Dataset"

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

    st.markdown("### Device Status")
    st.error("ESP32 Offline")
    st.caption("Hardware under inspection")
    st.caption("Dashboard: Available")
    st.caption(f"Records: {len(df)}")

    st.divider()

    uploaded = st.file_uploader(
        "Import Monitoring CSV",
        type=["csv"]
    )

    if uploaded:
        try:
            imported = pd.read_csv(uploaded)
            st.session_state.data = prepare_data(imported)
            st.session_state.data_source = "Imported Monitoring Records"
            st.success("Records imported.")
            st.rerun()
        except Exception as e:
            st.error(str(e))

    if st.button("Refresh Dashboard", use_container_width=True):
        st.rerun()


latest = df.iloc[-1]

st.title("🌡️ Public Heat Stress Monitoring System")
st.caption("Environmental and Physiological Monitoring Platform")

st.markdown(
    f"**Last Updated:** {datetime.now().strftime('%d %B %Y | %H:%M:%S')}"
)

if page == "Dashboard":

    st.subheader("Environmental Parameters")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric("Temperature", f"{latest['Temperature']:.1f}", "°C")

    with c2:
        metric("Humidity", f"{latest['Humidity']:.1f}", "%")

    with c3:
        metric("Atmospheric Pressure", f"{latest['Pressure']:.1f}", "hPa")

    st.subheader("Physiological Parameters")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric("Heart Rate", f"{latest['Heart_Rate']:.0f}", "BPM")

    with c2:
        spo2 = latest["SpO2"]
        metric(
            "SpO₂",
            f"{spo2:.1f}" if pd.notna(spo2) else "N/A",
            "%"
        )

    with c3:
        metric("Heat Index", f"{latest['Heat_Index']:.1f}", "°C")

    st.subheader("Risk Analysis")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Heat Stress Risk")
        st.warning(str(latest["Heat_Risk"]))

    with c2:
        st.markdown("### Physiological Indicator")
        st.info(str(latest["Health_Risk"]))

    st.subheader("Environmental Trend")

    fig = px.line(
        df.tail(30),
        x="Timestamp",
        y="Temperature",
        template="plotly_dark",
        title="Temperature Monitoring"
    )

    st.plotly_chart(fig, use_container_width=True)

elif page == "Live Data":

    st.subheader("Monitoring Records")

    st.dataframe(
        df.tail(30).sort_values(
            "Timestamp", ascending=False
        ),
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

    selected = st.selectbox(
        "Select Parameter",
        variables
    )

    fig = px.line(
        df,
        x="Timestamp",
        y=selected,
        template="plotly_dark",
        title=f"{selected} Trend"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(
        df,
        x="Temperature",
        y="Humidity",
        color="Heat_Risk",
        template="plotly_dark",
        title="Temperature vs Humidity"
    )

    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(
        df,
        x="Timestamp",
        y=["Temperature", "Humidity"],
        template="plotly_dark",
        title="Environmental Parameters"
    )

    st.plotly_chart(fig3, use_container_width=True)

elif page == "Alert History":

    st.subheader("Risk Alert History")

    alerts = df[
        (df["Heat_Risk"].isin(["High", "Very High"]))
        | (df["Health_Risk"] == "Elevated")
    ]

    if alerts.empty:
        st.success("No alert conditions in the available records.")
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

elif page == "Data Records":

    st.subheader("Monitoring Database")

    st.dataframe(
        df.sort_values(
            "Timestamp", ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Monitoring Records",
        csv,
        "heat_stress_records.csv",
        "text/csv",
        use_container_width=True
    )

elif page == "ML Model":

    st.subheader("Machine Learning Analysis")

    st.markdown("""
    The proposed machine-learning module is intended to
    analyse environmental and physiological parameters.

    **Input Features**
    - Temperature
    - Humidity
    - Heat Index
    - Heart Rate
    - SpO₂

    **Proposed Development**
    - Dataset preparation
    - Data preprocessing
    - Feature extraction
    - Model training
    - Model evaluation
    - Risk prediction
    """)

    st.info("Current displayed risk categories use rule-based thresholds. A trained ML model has not yet been integrated.")

    st.write("Heat Risk:", latest["Heat_Risk"])
    st.write("Physiological Indicator:", latest["Health_Risk"])

elif page == "Device Status":

    st.subheader("Hardware Device Information")

    st.error("ESP32: OFFLINE")

    st.write("Microcontroller: ESP32 DevKit")
    st.write("Environmental Sensor: BME280")
    st.write("Physiological Sensor: MAX30102")
    st.write("Display: 0.96-inch OLED")
    st.write("Communication: Wi-Fi")
    st.write("Hardware Condition: Under Inspection")

    st.success("Streamlit Dashboard: Available")

elif page == "Project Info":

    st.subheader("About the Project")

    st.markdown("""
    ### Public Heat Stress Monitoring and Alert System

    The project focuses on monitoring environmental
    conditions and selected physiological parameters.

    **Hardware Components**
    - ESP32 Microcontroller
    - BME280 Environmental Sensor
    - MAX30102 Optical Sensor
    - OLED Display
    - LED Indicator
    - Buzzer

    **Software Technologies**
    - Python
    - Streamlit
    - Pandas
    - NumPy
    - Plotly
    - IoT Communication

    **Project Objectives**
    - Environmental monitoring
    - Physiological monitoring
    - Heat index calculation
    - Risk classification
    - Historical data visualization
    - Remote monitoring interface
    """)

st.divider()

st.caption(
    "Public Heat Stress Monitoring System | "
    "Electronics and Telecommunication Engineering"
)