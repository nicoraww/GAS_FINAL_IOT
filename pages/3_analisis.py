import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import (GLOBAL_CSS, NIVELES, ORDEN_NIVELES, get_nivel,
                   get_historical, calc_metricas, sidebar_nav)

st.set_page_config(page_title="Análisis · Gas Monitor", page_icon="🔬", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
sidebar_nav()

st.markdown("""
<div style='padding:1.5rem 0 1rem 0;'>
    <div style='font-family:Space Mono,monospace;font-size:0.7rem;color:#475569;
                letter-spacing:0.15em;text-transform:uppercase;'>Análisis</div>
    <h1 style='margin:0.25rem 0 0 0;font-size:2rem;'>Análisis de Exposición</h1>
</div>
""", unsafe_allow_html=True)

col_r1, col_r2 = st.columns([2,1])
with col_r1:
    rango = st.selectbox("Rango", ["24h","7d","14d","30d"], index=1, label_visibility="visible")
with col_r2:
    umbral_z = st.slider("Umbral Z-score", 1.5, 3.5, 2.5, 0.1)

horas_map = {"24h":24,"7d":168,"14d":336,"30d":720}
horas = horas_map[rango]

df = get_historical(horas)
met = calc_metricas(df)

if df.empty:
    st.warning("Sin datos. Inicia el Wokwi para comenzar a generar lecturas.")
    st.stop()

tabs = st.tabs(["📐 Dosis acumulada", "🔄 Tendencias", "⚠️ Anomalías", "📅 Por día"])

# ─── TAB 1: AUC ───────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("### Dosis acumulada (AUC) — Exposición total de las placas")
    st.markdown("""
    <div style='background:#0f0f1e;border:1px solid #1e1e35;border-left:3px solid #f97316;
                border-radius:10px;padding:1rem 1.25rem;margin-bottom:1rem;
                font-size:0.82rem;color:#94a3b8;line-height:1.7;'>
        <strong style='color:#f8fafc;'>AUC (Area Under Curve)</strong>: integral de concentración × tiempo.
        Mide cuánto gas han recibido realmente las placas — no solo el pico, sino la exposición acumulada total.
        Unidad: <strong style='color:#f97316;'>ppm · minuto</strong>
    </div>
    """, unsafe_allow_html=True)

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Dosis AUC total",     f"{met['auc_ppm_min']:,.0f} ppm·min")
    m2.metric("Días activos",        f"{met['dias_activos']} días")
    m3.metric("Horas nivel ALTO+",   f"{met['tiempo_severo_h']} h")
    m4.metric("Pico máximo",         f"{met['pico_ppm']:.0f} ppm")

    # AUC por día
    auc_dias = {}
    prom_dias = {}
    for fecha, grupo in df.groupby("fecha"):
        g = grupo["gas_ppm"].dropna()
        if len(g) > 1:
            t = grupo["timestamp"].astype(np.int64) / 1e9
            auc_dias[fecha] = abs(float(np.trapz(g.values, t.values))) / 60
        else:
            auc_dias[fecha] = 0
        prom_dias[fecha] = float(g.mean())

    fechas  = list(auc_dias.keys())
    aucs    = list(auc_dias.values())
    proms   = list(prom_dias.values())

    def clasificar_dia(auc):
        if auc < 50_000:    return "Sin actividad", "#334155"
        if auc < 300_000:   return "Exposición baja", "#22c55e"
        if auc < 1_000_000: return "Exposición media", "#f97316"
        return "Exposición alta", "#ef4444"

    clases   = [clasificar_dia(a) for a in aucs]
    col_bars = [c[1] for c in clases]

    fig_auc = make_subplots(rows=2, cols=1, shared_xaxes=True,
                             subplot_titles=["AUC por día (ppm·min)", "Promedio diario (ppm)"],
                             vertical_spacing=0.12)
    fig_auc.add_trace(go.Bar(
        x=[str(f) for f in fechas], y=aucs,
        marker_color=col_bars, opacity=0.85, name="AUC"
    ), row=1, col=1)
    fig_auc.add_trace(go.Bar(
        x=[str(f) for f in fechas], y=proms,
        marker_color=[NIVELES.get(get_nivel(p)[0], NIVELES["CRITICO"])["color"] for p in proms],
        opacity=0.85, name="Promedio ppm"
    ), row=2, col=1)
    fig_auc.update_layout(paper_bgcolor="#080810", plot_bgcolor="#0f0f1e",
                          font=dict(color="#64748b"), height=380,
                          margin=dict(l=10,r=10,t=30,b=10), showlegend=False)
    fig_auc.update_yaxes(gridcolor="#1e1e35")
    fig_auc.update_xaxes(tickangle=45, tickfont=dict(size=9))
    st.plotly_chart(fig_auc, use_container_width=True)

    # Pie de clasificación
    from collections import Counter
    clase_counts = Counter([c[0] for c in clases])
    clase_colors = {"Sin actividad":"#334155","Exposición baja":"#22c55e",
                    "Exposición media":"#f97316","Exposición alta":"#ef4444"}
    col_pie, col_leg = st.columns([1,1])
    with col_pie:
        fig_p = go.Figure(go.Pie(
            labels=list(clase_counts.keys()),
            values=list(clase_counts.values()),
            marker=dict(colors=[clase_colors.get(k,"#64748b") for k in clase_counts.keys()],
                        line=dict(color="#080810",width=2)),
            hole=0.55, textfont=dict(family="Space Mono", size=10)
        ))
        fig_p.update_layout(paper_bgcolor="#080810", height=260,
                             margin=dict(l=0,r=0,t=20,b=0),
                             legend=dict(bgcolor="#0f0f1e", font=dict(color="#94a3b8",size=10)))
        st.plotly_chart(fig_p, use_container_width=True)
    with col_leg:
        st.markdown("**Clasificación de días por intensidad**")
        for label, color in clase_colors.items():
            count = clase_counts.get(label, 0)
            st.markdown(f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid #1e1e35;"><div style="width:12px;height:12px;border-radius:3px;background:{color};"></div><span style="font-size:0.82rem;color:#94a3b8;">{label}</span><span style="margin-left:auto;font-family:Space Mono,monospace;font-size:0.82rem;color:#f8fafc;">{count} días</span></div>', unsafe_allow_html=True)

# ─── TAB 2: Tendencias ────────────────────────────────────────────────────────
with tabs[1]:
    st.markdown("### Media móvil y tendencia de exposición")

    serie = df["gas_ppm"]
    rm5   = serie.rolling(window=5,  center=True).mean()
    rm60  = serie.rolling(window=60, center=True).mean()

    fig_mm = go.Figure()
    fig_mm.add_trace(go.Scatter(x=df["timestamp"], y=serie,
        name="Crudo", line=dict(color="#f97316",width=0.8), opacity=0.25))
    fig_mm.add_trace(go.Scatter(x=df["timestamp"], y=rm5,
        name="MM 5 min", line=dict(color="#f97316",width=1.8), opacity=0.85))
    fig_mm.add_trace(go.Scatter(x=df["timestamp"], y=rm60,
        name="MM 60 min (tendencia)", line=dict(color="#f8fafc",width=2.5)))
    fig_mm.add_hline(y=serie.mean(), line_dash="dot", line_color="#64748b",
                     line_width=1, annotation_text=f"Media {serie.mean():.0f}ppm")

    for nombre, data in NIVELES.items():
        if nombre != "SEGURO":
            fig_mm.add_hline(y=data["min"], line_dash="dot",
                             line_color=data["color"], line_width=0.7, opacity=0.4)

    fig_mm.update_layout(paper_bgcolor="#080810", plot_bgcolor="#0f0f1e",
                         font=dict(color="#64748b"), height=350,
                         margin=dict(l=10,r=10,t=20,b=10),
                         legend=dict(bgcolor="#0f0f1e", bordercolor="#1e1e35"))
    fig_mm.update_yaxes(gridcolor="#1e1e35")
    fig_mm.update_xaxes(gridcolor="#1e1e35")
    st.plotly_chart(fig_mm, use_container_width=True)

    # Tasa de cambio
    st.markdown("### Tasa de cambio — Detección de inicio de sesiones")
    df["tasa_cambio"] = df["gas_ppm"].diff()
    top5 = df.nlargest(5, "tasa_cambio")[["timestamp","gas_ppm","tasa_cambio","nivel"]]

    fig_tc = go.Figure()
    fig_tc.add_trace(go.Scatter(x=df["timestamp"], y=df["tasa_cambio"],
        name="Δppm/min", line=dict(color="#3b82f6",width=1.2), fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)"))
    fig_tc.add_hline(y=0, line_color="#334155", line_width=1)
    fig_tc.add_trace(go.Scatter(
        x=top5["timestamp"], y=top5["tasa_cambio"],
        mode="markers", marker=dict(color="#facc15", size=10, symbol="star"),
        name="Top 5 picos"
    ))
    fig_tc.update_layout(paper_bgcolor="#080810", plot_bgcolor="#0f0f1e",
                         font=dict(color="#64748b"), height=250,
                         margin=dict(l=10,r=10,t=20,b=10))
    fig_tc.update_yaxes(gridcolor="#1e1e35")
    st.plotly_chart(fig_tc, use_container_width=True)

    st.markdown("**Top 5 aumentos más bruscos (posibles inicios de sesión)**")
    st.dataframe(top5.rename(columns={"timestamp":"Fecha/Hora","gas_ppm":"PPM",
                                       "tasa_cambio":"Δ ppm/min","nivel":"Nivel"}),
                 use_container_width=True, hide_index=True)

# ─── TAB 3: Anomalías ────────────────────────────────────────────────────────
with tabs[2]:
    st.markdown(f"### Detección de anomalías por Z-score (umbral: ±{umbral_z})")

    serie = df["gas_ppm"].dropna()
    z     = (serie - serie.mean()) / serie.std()
    anom  = serie[z.abs() > umbral_z]

    fig_z = go.Figure()
    fig_z.add_trace(go.Scatter(x=df["timestamp"], y=serie,
        name="gas_ppm", line=dict(color="#f97316",width=1.2), opacity=0.8))
    fig_z.add_trace(go.Scatter(x=anom.index if hasattr(anom.index,'dtype') else df.loc[anom.index,"timestamp"],
        y=anom.values, mode="markers",
        marker=dict(color="#facc15",size=8,symbol="circle-open",line=dict(width=2)),
        name=f"Anomalías ({len(anom)})"))

    ub = serie.mean() + umbral_z * serie.std()
    lb = max(0, serie.mean() - umbral_z * serie.std())
    fig_z.add_hrect(y0=lb, y1=ub, fillcolor="rgba(249,115,22,0.05)",
                    line_width=0, annotation_text="Zona normal")
    fig_z.add_hline(y=ub, line_dash="dot", line_color="#ef4444", line_width=1)
    fig_z.add_hline(y=lb, line_dash="dot", line_color="#ef4444", line_width=1)

    fig_z.update_layout(paper_bgcolor="#080810", plot_bgcolor="#0f0f1e",
                        font=dict(color="#64748b"), height=320,
                        margin=dict(l=10,r=10,t=20,b=10),
                        legend=dict(bgcolor="#0f0f1e"))
    fig_z.update_yaxes(gridcolor="#1e1e35")
    st.plotly_chart(fig_z, use_container_width=True)

    col_a1, col_a2 = st.columns(2)
    col_a1.metric("Anomalías detectadas", len(anom))
    col_a2.metric("% del total", f"{len(anom)/len(serie)*100:.1f}%")

    if len(anom) > 0:
        anom_df = df.loc[df["gas_ppm"].isin(anom.values)][["timestamp","gas_ppm","nivel"]].head(20)
        anom_df["z_score"] = ((anom_df["gas_ppm"] - serie.mean()) / serie.std()).round(2)
        st.dataframe(anom_df.rename(columns={"timestamp":"Fecha/Hora","gas_ppm":"PPM","nivel":"Nivel","z_score":"Z-score"}),
                     use_container_width=True, hide_index=True)

# ─── TAB 4: Por día ──────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown("### Análisis por franjas horarias")

    df["hora"] = df["timestamp"].dt.hour
    def franja(h):
        if 6 <= h < 12:  return "Mañana (6–12h)"
        if 12 <= h < 18: return "Tarde (12–18h)"
        return "Noche (18–6h)"
    df["franja"] = df["hora"].apply(franja)

    resumen_franja = df.groupby("franja")["gas_ppm"].agg(["mean","max","count"]).round(1)
    resumen_franja.columns = ["Promedio ppm","Pico ppm","Lecturas"]

    fig_f = px.bar(resumen_franja.reset_index(), x="franja", y="Promedio ppm",
                   color="Promedio ppm", color_continuous_scale=["#22c55e","#f97316","#a855f7"],
                   title="Promedio de gas_ppm por franja horaria")
    fig_f.update_layout(paper_bgcolor="#080810", plot_bgcolor="#0f0f1e",
                        font=dict(color="#64748b"), height=280, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig_f, use_container_width=True)
    st.dataframe(resumen_franja, use_container_width=True)
