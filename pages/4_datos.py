import streamlit as st
import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import GLOBAL_CSS, ORDEN_NIVELES, NIVELES, get_historical, sidebar_nav

st.set_page_config(page_title="Datos · Gas Monitor", page_icon="🗄️", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
sidebar_nav()

st.markdown("""
<div style='padding:1.5rem 0 1rem 0;'>
    <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;
                letter-spacing:0.15em;text-transform:uppercase;'>Explorador</div>
    <h1 style='margin:0.25rem 0 0 0;font-size:2rem;'>Datos Crudos</h1>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    rango = st.selectbox("Rango", ["1h","6h","24h","7d","30d"], index=2)
with col2:
    nivel_filtro = st.multiselect("Filtrar niveles", ORDEN_NIVELES, default=ORDEN_NIVELES)
with col3:
    max_rows = st.selectbox("Filas a mostrar", [50, 100, 500, 1000, "Todas"], index=1)

horas_map = {"1h":1,"6h":6,"24h":24,"7d":168,"30d":720}
horas = horas_map[rango]
df = get_historical(horas)

if df.empty:
    st.info("Sin datos. Corre el Wokwi para generar lecturas.")
    st.stop()

# Filtrar por nivel
if nivel_filtro:
    df = df[df["nivel"].isin(nivel_filtro)]

# Limitar filas
if max_rows != "Todas":
    df_show = df.tail(int(max_rows))
else:
    df_show = df

# Métricas rápidas
c1,c2,c3,c4 = st.columns(4)
c1.metric("Registros filtrados", f"{len(df):,}")
c2.metric("Rango temporal", f"{(df['timestamp'].max()-df['timestamp'].min()).days} días")
c3.metric("PPM promedio", f"{df['gas_ppm'].mean():.0f}")
c4.metric("PPM máximo", f"{df['gas_ppm'].max():.0f}")

st.markdown("---")

# Tabla
df_display = df_show[["timestamp","gas_ppm","nivel","nivel_num","fecha"]].copy()
df_display["timestamp"] = df_display["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
df_display["gas_ppm"]   = df_display["gas_ppm"].round(1)
df_display = df_display.rename(columns={
    "timestamp": "Fecha/Hora", "gas_ppm": "PPM",
    "nivel": "Nivel", "nivel_num": "Índice", "fecha": "Fecha"
})

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True,
    height=500,
    column_config={
        "PPM":    st.column_config.NumberColumn(format="%.1f ppm"),
        "Índice": st.column_config.NumberColumn(format="%d"),
    }
)

# Descargar
csv = df[["timestamp","gas_ppm","nivel","nivel_num"]].to_csv(index=False)
st.download_button(
    label="⬇️ Descargar CSV",
    data=csv,
    file_name=f"gas_camara_{rango}.csv",
    mime="text/csv"
)

# Info del bucket
st.markdown("---")
st.markdown("""
<div style='background:#0f0f1e;border:1px solid #1e1e35;border-radius:12px;
            padding:1.25rem;font-family:Space Mono,monospace;font-size:0.78rem;
            color:#475569;line-height:2;'>
    <div style='color:#22c55e;margin-bottom:0.5rem;'>INFLUXDB · IOTHENRY</div>
    measurement: gas_camara &nbsp;|&nbsp;
    field: gas_ppm &nbsp;|&nbsp;
    tags: dispositivo=ESP32-Wokwi, ubicacion=camara<br>
    org: 91eabda09bdf6a8e &nbsp;|&nbsp;
    url: us-east-1-1.aws.cloud2.influxdata.com &nbsp;|&nbsp;
    retention: 30 días
</div>
""", unsafe_allow_html=True)
