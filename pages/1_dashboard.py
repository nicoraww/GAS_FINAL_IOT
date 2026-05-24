import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import (GLOBAL_CSS, NIVELES, ORDEN_NIVELES, get_nivel,
                   get_latest, get_historical, calc_metricas, sidebar_nav)

st.set_page_config(page_title="Dashboard · Gas Monitor", page_icon="📊", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
sidebar_nav()

# ─── Header ───────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
    <div style='padding:1.5rem 0 1rem 0;'>
        <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;
                    letter-spacing:0.15em;text-transform:uppercase;'>Dashboard</div>
        <h1 style='margin:0.25rem 0 0 0;font-size:2rem;'>Cámara de Gas</h1>
    </div>
    """, unsafe_allow_html=True)
with col_h2:
    rango = st.selectbox("Rango", ["1h","6h","24h","7d","30d"], index=2, label_visibility="collapsed")
    horas_map = {"1h":1,"6h":6,"24h":24,"7d":168,"30d":720}
    horas = horas_map[rango]
    auto = st.toggle("Auto 5s", value=False)

# ─── Cargar datos ─────────────────────────────────────────────────────────────
latest = get_latest()
df     = get_historical(horas)
met    = calc_metricas(df)

ppm_actual   = latest if latest is not None else 0
nivel_n, nivel_c, nivel_i = get_nivel(ppm_actual)

# Alerta banner
if nivel_i >= 4:
    st.markdown(f"""
    <div style='background:{nivel_c}18;border:1px solid {nivel_c}55;border-radius:10px;
                padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.85rem;color:{nivel_c};font-weight:500;'>
        ⚠️ ALERTA — Nivel <strong>{nivel_n}</strong> detectado · {ppm_actual:.0f} ppm en tiempo real
    </div>
    """, unsafe_allow_html=True)

# ─── GAUGES ───────────────────────────────────────────────────────────────────
st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.75rem;">● Lecturas en tiempo real</div>', unsafe_allow_html=True)

def make_gauge(value, title, max_val, color, suffix=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 12, "color": "#64748b", "family": "Space Mono"}},
        number={"suffix": suffix, "font": {"size": 26, "color": "#f8fafc", "family": "Space Mono"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#1e1e35",
                     "tickfont": {"color": "#334155", "size": 9}},
            "bar":  {"color": color, "thickness": 0.25},
            "bgcolor": "#0f0f1e",
            "bordercolor": "#1e1e35", "borderwidth": 1,
            "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.8, "value": value}
        }
    ))
    fig.update_layout(paper_bgcolor="#080810", plot_bgcolor="#080810",
                      height=200, margin=dict(l=20,r=20,t=40,b=10))
    return fig

cg1, cg2, cg3 = st.columns(3)
with cg1:
    st.plotly_chart(make_gauge(ppm_actual, "GAS PPM", 10000, nivel_c, " ppm"),
                    use_container_width=True, key="gauge_ppm")
    st.markdown(f'<div style="text-align:center;margin-top:-8px;"><span style="background:{nivel_c}22;color:{nivel_c};border:1px solid {nivel_c}44;padding:3px 12px;border-radius:999px;font-family:Space Mono,monospace;font-size:0.72rem;font-weight:700;">● {nivel_n}</span></div>', unsafe_allow_html=True)

with cg2:
    idx_val = nivel_i
    st.plotly_chart(make_gauge(idx_val, "NIVEL ÍNDICE (0–5)", 5, nivel_c),
                    use_container_width=True, key="gauge_idx")

with cg3:
    pct = min(100, (ppm_actual / 10000) * 100)
    st.plotly_chart(make_gauge(pct, "EXPOSICIÓN %", 100, nivel_c, "%"),
                    use_container_width=True, key="gauge_pct")

# ─── KPIs ─────────────────────────────────────────────────────────────────────
st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;letter-spacing:0.15em;text-transform:uppercase;margin:1.5rem 0 0.75rem 0;">● Métricas de exposición</div>', unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("Días activos",      f"{met.get('dias_activos',0)} días")
k2.metric("Dosis AUC",         f"{met.get('auc_ppm_min',0):,.0f} ppm·min")
k3.metric("Tiempo ALTO+",      f"{met.get('tiempo_severo_h',0)} h")
k4.metric("Pico máximo",       f"{met.get('pico_ppm',0):.0f} ppm")
k5.metric("Promedio",          f"{met.get('promedio_ppm',0):.0f} ppm")

# ─── Serie de tiempo ──────────────────────────────────────────────────────────
if not df.empty:
    st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;letter-spacing:0.15em;text-transform:uppercase;margin:1.5rem 0 0.75rem 0;">● Serie temporal — Concentración de gas</div>', unsafe_allow_html=True)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.75, 0.25], vertical_spacing=0.04)

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["gas_ppm"],
        name="gas_ppm", line=dict(color="#f97316", width=1.5),
        fill="tozeroy", fillcolor="rgba(249,115,22,0.08)"
    ), row=1, col=1)

    fig.add_hline(y=df["gas_ppm"].mean(), line_dash="dot",
                  line_color="#64748b", line_width=1, row=1, col=1)

    for nombre, data in NIVELES.items():
        if nombre != "SEGURO":
            fig.add_hline(y=data["min"], line_dash="dot",
                          line_color=data["color"], line_width=0.6,
                          opacity=0.5, row=1, col=1)

    colors_bar = [NIVELES.get(n, NIVELES["CRITICO"])["color"] for n in df["nivel"]]
    fig.add_trace(go.Bar(
        x=df["timestamp"], y=df["nivel_num"],
        marker_color=colors_bar, opacity=0.8, name="Nivel"
    ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="#080810", plot_bgcolor="#0f0f1e",
        font=dict(color="#64748b", family="Sora"),
        height=380, margin=dict(l=10,r=10,t=10,b=10),
        legend=dict(bgcolor="#0f0f1e", bordercolor="#1e1e35"),
        hovermode="x unified", showlegend=False
    )
    fig.update_yaxes(gridcolor="#1e1e35", zerolinecolor="#1e1e35")
    fig.update_xaxes(gridcolor="#1e1e35")
    st.plotly_chart(fig, use_container_width=True)

# ─── Distribución ─────────────────────────────────────────────────────────────
if not df.empty:
    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.75rem;">● Distribución por nivel</div>', unsafe_allow_html=True)
        conteo = df["nivel"].value_counts()
        labels = [n for n in ORDEN_NIVELES if n in conteo.index]
        values = [conteo[n] for n in labels]
        colors = [NIVELES[n]["color"] for n in labels]

        fig_pie = go.Figure(go.Pie(
            labels=labels, values=values,
            marker=dict(colors=colors, line=dict(color="#080810", width=2)),
            hole=0.6, textfont=dict(family="Space Mono", size=10),
        ))
        fig_pie.add_annotation(text=f"<b>{sum(values):,}</b>", x=0.5, y=0.5,
                                font_size=18, showarrow=False,
                                font=dict(color="#f8fafc", family="Space Mono"))
        fig_pie.update_layout(paper_bgcolor="#080810", height=280,
                              margin=dict(l=0,r=0,t=20,b=0),
                              legend=dict(bgcolor="#0f0f1e", bordercolor="#1e1e35",
                                          font=dict(color="#94a3b8", size=10)))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_d2:
        st.markdown('<div style="font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.75rem;">● Resumen estadístico</div>', unsafe_allow_html=True)
        rows = [
            ("Total lecturas",   f"{met.get('total_lecturas',0):,}"),
            ("Promedio PPM",     f"{met.get('promedio_ppm',0):.0f}"),
            ("Pico máximo",      f"{met.get('pico_ppm',0):.0f}"),
            ("Mínimo",           f"{met.get('min_ppm',0):.0f}"),
            ("Desv. estándar",   f"{met.get('std_ppm',0):.0f}"),
            ("IQR",              f"{met.get('iqr',0):.0f}"),
            ("Días activos",     f"{met.get('dias_activos',0)}"),
            ("Horas ALTO+",      f"{met.get('tiempo_severo_h',0)} h"),
            ("AUC total",        f"{met.get('auc_ppm_min',0):,.0f} ppm·min"),
        ]
        for key, val in rows:
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;padding:0.45rem 0;
                        border-bottom:1px solid #1e1e35;'>
                <span style='color:#64748b;font-size:0.82rem;'>{key}</span>
                <span style='font-family:Space Mono,monospace;font-size:0.85rem;
                             font-weight:600;color:#f8fafc;'>{val}</span>
            </div>
            """, unsafe_allow_html=True)

if auto:
    import time; time.sleep(5); st.rerun()
