# 🧪 Sistema de Monitoreo de Cámara de Gas

Plataforma de monitoreo IoT en tiempo real para análisis de exposición a gas en cámaras de prueba de resistencia de materiales.

**Stack:** ESP32 + MQ2 (Wokwi) → InfluxDB Cloud → Grafana + Streamlit

---

## 📁 Estructura

```
gas-camara-monitor/
├── app.py                    # Página de inicio / resumen del proyecto
├── utils.py                  # Conexión InfluxDB, helpers, CSS global
├── requirements.txt
├── .streamlit/
│   └── config.toml           # Tema oscuro
└── pages/
    ├── 1_dashboard.py        # Dashboard principal con gauges y KPIs
    ├── 2_tiempo_real.py      # Monitor en vivo con auto-refresh
    ├── 3_analisis.py         # AUC, tendencias, anomalías, franjas
    └── 4_datos.py            # Explorador de datos + descarga CSV
```

## 🚀 Despliegue en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. **New app** → selecciona el repo → main file: `app.py`
4. Deploy

## 💻 Correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📡 Datos

- **InfluxDB:** `us-east-1-1.aws.cloud2.influxdata.com`
- **Bucket:** `IOTHENRY`
- **Measurement:** `gas_camara`
- **Campo:** `gas_ppm`
- **Tags:** `dispositivo=ESP32-Wokwi`, `ubicacion=camara`

## 🚦 Niveles de alerta (MQ2)

| Nivel | Rango | Color |
|---|---|---|
| SEGURO | 0–800 ppm | 🟢 Verde |
| TRAZA | 800–1,500 ppm | 🔵 Azul |
| LEVE | 1,500–3,000 ppm | 🟡 Amarillo |
| MODERADO | 3,000–5,000 ppm | 🟠 Naranja |
| ALTO | 5,000–7,500 ppm | 🔴 Rojo |
| CRÍTICO | 7,500–10,000 ppm | 🟣 Morado |

---

EAFIT · Ingeniería IoT · 2026
