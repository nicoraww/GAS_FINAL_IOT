import pandas as pd
import numpy as np
import streamlit as st
from influxdb_client import InfluxDBClient

# ─── Credenciales ─────────────────────────────────────────────────────────────
INFLUX_URL    = "https://us-east-1-1.aws.cloud2.influxdata.com"
INFLUX_TOKEN  = "g84PQSAsH11VRlyJqeopT4DsWqioG3axcCTDw6H2nxWo637DAQr_76M3ziJO3VKgTTMpvu9D3c8Yg8JV5l4PJw=="
INFLUX_ORG    = "91eabda09bdf6a8e"
INFLUX_BUCKET = "IOTHENRY"

# ─── Niveles ──────────────────────────────────────────────────────────────────
NIVELES = {
    "SEGURO":   {"color": "#22c55e", "min": 0,    "max": 800,   "idx": 0},
    "TRAZA":    {"color": "#3b82f6", "min": 800,  "max": 1500,  "idx": 1},
    "LEVE":     {"color": "#eab308", "min": 1500, "max": 3000,  "idx": 2},
    "MODERADO": {"color": "#f97316", "min": 3000, "max": 5000,  "idx": 3},
    "ALTO":     {"color": "#ef4444", "min": 5000, "max": 7500,  "idx": 4},
    "CRITICO":  {"color": "#a855f7", "min": 7500, "max": 10001, "idx": 5},
}
ORDEN_NIVELES = ["SEGURO", "TRAZA", "LEVE", "MODERADO", "ALTO", "CRITICO"]

def get_nivel(ppm):
    for nombre, data in NIVELES.items():
        if data["min"] <= ppm < data["max"]:
            return nombre, data["color"], data["idx"]
    return "CRITICO", "#a855f7", 5

# ─── CSS Global ───────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"], .stApp {
    font-family: 'Sora', sans-serif;
    background-color: #080810;
    color: #e2e8f0;
}
[data-testid="stSidebar"] { background: #0d0d1a !important; border-right: 1px solid #1e1e35; }
div[data-testid="metric-container"] {
    background: #0f0f1e; border: 1px solid #1e1e35; border-radius: 12px; padding: 1rem 1.25rem;
}
h1, h2, h3 { font-family: 'Space Mono', monospace !important; letter-spacing: -0.02em; }
.stTabs [data-baseweb="tab-list"] { background: #0f0f1e; border-radius: 12px; padding: 4px; border: 1px solid #1e1e35; }
.stTabs [data-baseweb="tab"] { font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #64748b; border-radius: 8px; }
.stTabs [aria-selected="true"] { background: #1e1e35 !important; color: #f8fafc !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.card { background: #0f0f1e; border: 1px solid #1e1e35; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
</style>
"""

# ─── Cliente InfluxDB ─────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)

def query_influx(flux_query):
    try:
        client = get_client()
        tables = client.query_api().query(flux_query)
        records = []
        for table in tables:
            for record in table.records:
                records.append({
                    "time":  record.get_time(),
                    "field": record.get_field(),
                    "value": record.get_value(),
                })
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"❌ Error InfluxDB: {e}")
        return pd.DataFrame()

def get_latest():
    q = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -10m)
  |> filter(fn: (r) => r["_measurement"] == "gas_camara")
  |> filter(fn: (r) => r["_field"] == "gas_ppm")
  |> last()
'''
    df = query_influx(q)
    if df.empty:
        return None
    return float(df.iloc[0]["value"])

def get_historical(hours=24):
    q = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -{hours}h)
  |> filter(fn: (r) => r["_measurement"] == "gas_camara")
  |> filter(fn: (r) => r["_field"] == "gas_ppm")
'''
    df = query_influx(q)
    if df.empty:
        return pd.DataFrame()
    df = df.rename(columns={"time": "timestamp", "value": "gas_ppm"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert("America/Bogota")
    df = df.sort_values("timestamp").reset_index(drop=True)
    df["nivel"], df["color"], df["nivel_num"] = zip(*df["gas_ppm"].apply(get_nivel))
    df["fecha"] = df["timestamp"].dt.date
    return df

def calc_metricas(df):
    if df.empty or "gas_ppm" not in df.columns:
        return {}
    s = df["gas_ppm"]
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1

    dias_activos = 0
    if "fecha" in df.columns:
        dias_activos = df[df["gas_ppm"] > 1500].groupby("fecha").ngroups

    tiempo_severo_h = 0
    if len(df) > 1:
        df2 = df.sort_values("timestamp")
        df2["dt"] = df2["timestamp"].diff().dt.total_seconds().fillna(0)
        tiempo_severo_h = df2[df2["gas_ppm"] > 5000]["dt"].sum() / 3600

    auc = 0
    if len(df) > 1:
        t = df["timestamp"].astype(np.int64) / 1e9
        auc = abs(float(np.trapz(s.values, t))) / 60

    return {
        "dias_activos":      dias_activos,
        "pico_ppm":          float(s.max()),
        "promedio_ppm":      float(s.mean()),
        "min_ppm":           float(s.min()),
        "std_ppm":           float(s.std()),
        "tiempo_severo_h":   round(tiempo_severo_h, 2),
        "auc_ppm_min":       round(auc, 1),
        "total_lecturas":    len(df),
        "iqr":               round(iqr, 2),
    }

def sidebar_nav():
    with st.sidebar:
        st.markdown("""
        <div style='padding:1.5rem 0 1rem 0;'>
            <div style='font-family:Space Mono,monospace;font-size:1.1rem;font-weight:700;color:#f8fafc;'>
                🧪 GAS MONITOR
            </div>
            <div style='font-size:0.7rem;color:#475569;font-family:Space Mono,monospace;margin-top:4px;'>
                v1.0 · ESP32 + MQ2 · EAFIT
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("NAVEGACIÓN")
        st.page_link("app.py",                label="🏠  Inicio")
        st.page_link("pages/1_dashboard.py",  label="📊  Dashboard")
        st.page_link("pages/2_tiempo_real.py",label="⚡  Tiempo Real")
        st.page_link("pages/3_analisis.py",   label="🔬  Análisis")
        st.page_link("pages/4_datos.py",      label="🗄️  Datos")
        st.markdown("---")
        st.markdown("""
        <div style='font-size:0.7rem;color:#334155;font-family:Space Mono,monospace;line-height:1.8;'>
        📡 InfluxDB Cloud<br>🪣 IOTHENRY<br>🌎 us-east-1-1.aws
        </div>""", unsafe_allow_html=True)
