import streamlit as st
import plotly.graph_objects as go
import time, sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import (GLOBAL_CSS, NIVELES, ORDEN_NIVELES, get_nivel,
                   get_latest, get_historical, sidebar_nav)

st.set_page_config(page_title="Tiempo Real · Gas Monitor", page_icon="⚡", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
sidebar_nav()

st.markdown("""
<div style='padding:1.5rem 0 1rem 0;'>
    <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;
                letter-spacing:0.15em;text-transform:uppercase;'>Tiempo Real</div>
    <h1 style='margin:0.25rem 0 0 0;font-size:2rem;'>Monitor en Vivo</h1>
</div>
""", unsafe_allow_html=True)

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1,1,4])
with col_ctrl1:
    auto = st.toggle("⚡ Auto-refresh", value=True)
with col_ctrl2:
    intervalo = st.selectbox("Intervalo", ["5s","10s","30s"], label_visibility="collapsed")
    seg = int(intervalo.replace("s",""))

# ─── Lectura actual ───────────────────────────────────────────────────────────
ppm = get_latest()
ppm = ppm if ppm is not None else 0
nivel_n, nivel_c, nivel_i = get_nivel(ppm)

# Banner de estado
estado_icon = "🟢" if nivel_i == 0 else "🔵" if nivel_i == 1 else "🟡" if nivel_i == 2 else "🟠" if nivel_i == 3 else "🔴" if nivel_i == 4 else "🟣"
st.markdown(f"""
<div style='background:{nivel_c}15;border:1px solid {nivel_c}40;border-radius:12px;
            padding:1.25rem 1.5rem;margin-bottom:1.5rem;display:flex;
            align-items:center;gap:1rem;'>
    <div style='font-size:2.5rem;'>{estado_icon}</div>
    <div>
        <div style='font-family:Space Mono,monospace;font-size:1.8rem;
                    font-weight:700;color:{nivel_c};'>{ppm:.0f} ppm</div>
        <div style='font-family:Space Mono,monospace;font-size:0.85rem;
                    color:#64748b;margin-top:2px;'>Nivel: {nivel_n} · Índice: {nivel_i}/5</div>
    </div>
    <div style='margin-left:auto;text-align:right;'>
        <div style='font-size:0.7rem;color:#334155;font-family:Space Mono,monospace;'>ÚLTIMA LECTURA</div>
        <div style='font-size:0.85rem;color:#64748b;font-family:Space Mono,monospace;'>ESP32-Wokwi · camara</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Gauge grande ─────────────────────────────────────────────────────────────
col_gauge, col_info = st.columns([2, 1])

with col_gauge:
    steps = []
    boundaries = [0, 800, 1500, 3000, 5000, 7500, 10000]
    step_colors = ["#22c55e20","#3b82f620","#eab30820","#f9731620","#ef434420","#a855f720"]
    for i in range(len(boundaries)-1):
        steps.append({"range": [boundaries[i], min(boundaries[i+1], 10000)], "color": step_colors[i]})

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ppm,
        title={"text": "Concentración de Gas · Tiempo Real",
               "font": {"size": 14, "color": "#64748b", "family": "Space Mono"}},
        number={"suffix": " ppm", "font": {"size": 48, "color": "#f8fafc", "family": "Space Mono"}},
        delta={"reference": 5000, "increasing": {"color": "#ef4444"},
               "decreasing": {"color": "#22c55e"}},
        gauge={
            "axis": {"range": [0, 10000], "tickcolor": "#1e1e35",
                     "tickfont": {"color": "#334155", "size": 10}, "nticks": 6},
            "bar":  {"color": nivel_c, "thickness": 0.2},
            "bgcolor": "#0f0f1e",
            "bordercolor": "#1e1e35", "borderwidth": 1,
            "steps": steps,
            "threshold": {"line": {"color": nivel_c, "width": 4}, "thickness": 0.85, "value": ppm}
        }
    ))
    fig.update_layout(paper_bgcolor="#080810", plot_bgcolor="#080810",
                      height=340, margin=dict(l=30,r=30,t=50,b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:1rem;">● Escala de niveles</div>', unsafe_allow_html=True)

    for nombre in ORDEN_NIVELES:
        data = NIVELES[nombre]
        is_active = nombre == nivel_n
        bg = f"{data['color']}20" if is_active else "transparent"
        border = f"1px solid {data['color']}60" if is_active else "1px solid #1e1e35"
        st.markdown(f"""
        <div style='background:{bg};border:{border};border-radius:8px;
                    padding:0.6rem 0.9rem;margin-bottom:0.4rem;
                    display:flex;align-items:center;gap:0.75rem;'>
            <div style='width:10px;height:10px;border-radius:50%;
                        background:{data["color"]};flex-shrink:0;'></div>
            <div>
                <div style='font-family:Space Mono,monospace;font-size:0.75rem;
                            font-weight:700;color:{"#f8fafc" if is_active else "#64748b"};'>{nombre}</div>
                <div style='font-size:0.65rem;color:#475569;'>{data["min"]}–{data["max"]} ppm</div>
            </div>
            {"<div style='margin-left:auto;font-family:Space Mono,monospace;font-size:0.65rem;color:" + data["color"] + ";'>◀ ACTUAL</div>" if is_active else ""}
        </div>
        """, unsafe_allow_html=True)

# ─── Últimas lecturas ──────────────────────────────────────────────────────────
st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;letter-spacing:0.15em;text-transform:uppercase;margin:1.5rem 0 0.75rem 0;">● Últimas 30 minutos</div>', unsafe_allow_html=True)

df30 = get_historical(1)
if not df30.empty:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df30["timestamp"], y=df30["gas_ppm"],
        mode="lines", name="gas_ppm",
        line=dict(color=nivel_c, width=2),
        fill="tozeroy", fillcolor=f"{nivel_c}15"
    ))
    fig2.add_hline(y=ppm, line_dash="dot", line_color=nivel_c, line_width=1.5)

    for nombre, data in NIVELES.items():
        if nombre != "SEGURO":
            fig2.add_hline(y=data["min"], line_dash="dot",
                           line_color=data["color"], line_width=0.7, opacity=0.4)

    fig2.update_layout(
        paper_bgcolor="#080810", plot_bgcolor="#0f0f1e",
        font=dict(color="#64748b", family="Sora"),
        height=220, margin=dict(l=10,r=10,t=10,b=10),
        showlegend=False, hovermode="x unified"
    )
    fig2.update_yaxes(gridcolor="#1e1e35", zerolinecolor="#1e1e35", range=[0, 10500])
    fig2.update_xaxes(gridcolor="#1e1e35")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Sin datos recientes. Inicia la simulación en Wokwi.")

if auto:
    time.sleep(seg)
    st.rerun()
