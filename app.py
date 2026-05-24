import streamlit as st

st.set_page_config(
    page_title="Cámara de Gas — Monitor",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS Global ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Sora', sans-serif;
    background-color: #080810;
    color: #e2e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1e1e35;
}
[data-testid="stSidebar"] .stMarkdown p {
    color: #64748b;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* Botones de navegación sidebar */
[data-testid="stSidebar"] .stButton button {
    width: 100%;
    background: transparent;
    border: 1px solid #1e1e35;
    color: #94a3b8;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    text-align: left;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #1e1e35;
    color: #f8fafc;
    border-color: #3b3b5c;
}

/* Cards */
.card {
    background: #0f0f1e;
    border: 1px solid #1e1e35;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.card-accent {
    border-left: 3px solid #22c55e;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: #0f0f1e;
    border: 1px solid #1e1e35;
    border-radius: 12px;
    padding: 1rem 1.25rem;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    letter-spacing: -0.02em;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0f0f1e;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1e1e35;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #64748b;
    border-radius: 8px;
}
.stTabs [aria-selected="true"] {
    background: #1e1e35 !important;
    color: #f8fafc !important;
}

/* Hide streamlit branding */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ─────────────────────────────────────────────────────────────────
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
    st.page_link("app.py",                       label="🏠  Inicio",          icon=None)
    st.page_link("pages/1_dashboard.py",          label="📊  Dashboard",       icon=None)
    st.page_link("pages/2_tiempo_real.py",        label="⚡  Tiempo Real",     icon=None)
    st.page_link("pages/3_analisis.py",           label="🔬  Análisis",        icon=None)
    st.page_link("pages/4_datos.py",              label="🗄️  Datos",           icon=None)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.7rem;color:#334155;font-family:Space Mono,monospace;line-height:1.8;'>
    📡 InfluxDB Cloud<br>
    🪣 Bucket: IOTHENRY<br>
    🌎 us-east-1-1.aws<br>
    ⏱️ Refresh: 5s
    </div>
    """, unsafe_allow_html=True)

# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:3rem 0 2rem 0;'>
    <div style='font-family:Space Mono,monospace;font-size:0.75rem;color:#22c55e;
                letter-spacing:0.2em;text-transform:uppercase;margin-bottom:0.75rem;'>
        EAFIT · Ingeniería IoT · 2026
    </div>
    <h1 style='font-size:2.8rem;font-weight:700;line-height:1.1;margin:0;
               background:linear-gradient(135deg,#f8fafc 0%,#94a3b8 100%);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        Sistema de Monitoreo<br>de Cámara de Gas
    </h1>
    <p style='color:#64748b;font-size:1rem;margin-top:1rem;max-width:600px;line-height:1.7;'>
        Plataforma de monitoreo en tiempo real para el análisis de exposición a gas
        en cámaras de prueba de resistencia de materiales. ESP32 + MQ2 → InfluxDB → Streamlit.
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Stack visual ─────────────────────────────────────────────────────────────
st.markdown("### Stack tecnológico")

col1, col2, col3, col4, col5 = st.columns(5)

stack = [
    ("🔌", "Wokwi", "ESP32 + MQ2\nSimulador IoT"),
    ("📡", "InfluxDB", "Time-series\nCloud Storage"),
    ("📊", "Grafana", "Dashboards\nTiempo real"),
    ("🐍", "Streamlit", "Análisis &\nVisualización"),
    ("📓", "Colab", "Análisis\nEstadístico"),
]

for col, (icon, title, desc) in zip([col1,col2,col3,col4,col5], stack):
    with col:
        st.markdown(f"""
        <div class='card' style='text-align:center;padding:1.25rem 1rem;'>
            <div style='font-size:1.8rem;margin-bottom:0.5rem;'>{icon}</div>
            <div style='font-family:Space Mono,monospace;font-size:0.85rem;
                        font-weight:700;color:#f8fafc;margin-bottom:0.25rem;'>{title}</div>
            <div style='font-size:0.7rem;color:#64748b;white-space:pre-line;line-height:1.5;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Arquitectura ─────────────────────────────────────────────────────────────
st.markdown("### Arquitectura del sistema")

st.markdown("""
<div class='card card-accent' style='font-family:Space Mono,monospace;font-size:0.8rem;line-height:2;color:#94a3b8;'>
    <div style='color:#22c55e;font-weight:700;margin-bottom:0.5rem;'>FLUJO DE DATOS</div>
    <span style='color:#f97316;'>Wokwi (ESP32+MQ2)</span>
    &nbsp;→&nbsp;
    <span style='color:#facc15;'>HTTPS cada 5s</span>
    &nbsp;→&nbsp;
    <span style='color:#3b82f6;'>InfluxDB Cloud (IOTHENRY)</span>
    &nbsp;→&nbsp;
    <span style='color:#a855f7;'>Grafana (gauges RT)</span>
    &nbsp;+&nbsp;
    <span style='color:#22c55e;'>Streamlit (análisis)</span>
    <br><br>
    <div style='color:#475569;'>
    measurement: gas_camara &nbsp;|&nbsp;
    fields: gas_ppm, nivel &nbsp;|&nbsp;
    tags: dispositivo=ESP32-Wokwi, ubicacion=camara
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Niveles ──────────────────────────────────────────────────────────────────
st.markdown("### Escala de niveles de exposición")

niveles = [
    ("SEGURO",   "#22c55e", "0–800 ppm",      "Sin presencia significativa de gas"),
    ("TRAZA",    "#3b82f6", "800–1,500 ppm",   "Presencia mínima detectada"),
    ("LEVE",     "#eab308", "1,500–3,000 ppm", "Exposición baja, monitoreo recomendado"),
    ("MODERADO", "#f97316", "3,000–5,000 ppm", "Sesión activa en curso"),
    ("ALTO",     "#ef4444", "5,000–7,500 ppm", "Concentración elevada, alerta técnica"),
    ("CRITICO",  "#a855f7", "7,500–10,000 ppm","Saturación, intervención inmediata"),
]

cols = st.columns(6)
for col, (nombre, color, rango, desc) in zip(cols, niveles):
    with col:
        st.markdown(f"""
        <div class='card' style='border-top:3px solid {color};padding:1rem;text-align:center;'>
            <div style='font-family:Space Mono,monospace;font-size:0.75rem;
                        font-weight:700;color:{color};margin-bottom:0.4rem;'>{nombre}</div>
            <div style='font-size:0.7rem;color:#94a3b8;font-family:Space Mono,monospace;
                        margin-bottom:0.4rem;'>{rango}</div>
            <div style='font-size:0.65rem;color:#475569;line-height:1.4;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Use Case ─────────────────────────────────────────────────────────────────
st.markdown("### Caso de uso")

col_a, col_b = st.columns([3, 2])
with col_a:
    st.markdown("""
    <div class='card'>
        <div style='font-family:Space Mono,monospace;font-size:0.75rem;color:#22c55e;
                    letter-spacing:0.1em;margin-bottom:1rem;'>DESCRIPCIÓN DEL PROYECTO</div>
        <p style='color:#94a3b8;font-size:0.9rem;line-height:1.8;margin:0;'>
            Una <strong style='color:#f8fafc;'>cámara de pruebas de resistencia al gas</strong>
            expone placas metálicas y materiales compuestos a gases controlados
            (GLP, metano, humo) para medir su degradación bajo exposición prolongada.
            <br><br>
            El sistema mide en tiempo real la concentración, acumula datos históricos
            y permite analizar <strong style='color:#f8fafc;'>cuánto gas han recibido
            las placas y por cuántos días</strong>, calculando la dosis acumulada (AUC)
            como métrica principal de exposición.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class='card'>
        <div style='font-family:Space Mono,monospace;font-size:0.75rem;color:#22c55e;
                    letter-spacing:0.1em;margin-bottom:1rem;'>CASOS DE USO</div>
        <div style='font-size:0.82rem;color:#94a3b8;line-height:2;'>
            <span style='color:#f97316;'>UC-01</span> · Monitoreo en tiempo real<br>
            <span style='color:#f97316;'>UC-02</span> · Exposición histórica por placa<br>
            <span style='color:#f97316;'>UC-03</span> · Comparación entre sesiones<br>
            <span style='color:#f97316;'>UC-04</span> · Reporte de cierre de sesión
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center;color:#1e1e35;font-size:0.7rem;
            font-family:Space Mono,monospace;padding:2rem 0 1rem 0;'>
    EAFIT · Ingeniería IoT · 2026 · ESP32 + MQ2 + InfluxDB + Streamlit
</div>
""", unsafe_allow_html=True)
