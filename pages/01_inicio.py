"""Página de inicio — Resumen ejecutivo y navegación rápida."""
import streamlit as st
from core.model import PREVALENCE, THRESHOLD
from core.styles import render_footer, render_hero

render_hero(
    eyebrow="Universidad del Cauca · Inteligencia de Datos",
    title="Sistema para la Predicción del Riesgo Coronario a 10 Años",
    subtitle=(
        "Herramienta clínica educativa basada en la cohorte de Framingham y el pipeline "
        "LogisticRegression (model_v1) con ingeniería de características clínicas."
    ),
    chips=[
        "LogisticRegression (class_weight)",
        "15 variables clínicas",
        "Evaluación individual y masiva CSV",
        "Uso educativo",
    ],
)

k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "PR-AUC (Test)", "0.2689", "Métrica primaria en desbalance"),
    (k2, "ROC-AUC (Test)", "0.6902", "Capacidad de discriminación"),
    (k3, "Umbral F2-óptimo", f"{THRESHOLD:.2%}", "Punto de corte de alto riesgo"),
    (k4, "Prevalencia cohorte", f"{PREVALENCE:.2%}", "Tasa base de CHD a 10 años"),
]
for col, label, val, sub in kpis:
    with col:
        st.markdown(
            f"""
<div class="kpi-card">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{val}</div>
  <div class="kpi-sub">{sub}</div>
</div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

st.markdown(
    """
<div class="ui-card">
  <div class="ui-card-eyebrow">Introducción</div>
  <h3>Explora el riesgo cardiovascular de forma clara e interpretable</h3>
  <p>
    Este entorno unifica la exploración de coeficientes reales del modelo, la evaluación individual con
    explicabilidad por paciente y el procesamiento por lotes mediante archivos CSV para análisis comparativos.
  </p>
</div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    st.markdown(
        """
<div class="ui-card" style="min-height: 175px;">
  <h3>📊 Dashboard del modelo</h3>
  <p>Inspecciona los Odds Ratios reales de <code>model_v1</code> y simula cómo cambia el riesgo según edad, presión sistólica y tabaquismo.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/02_dashboard.py", label="Abrir Dashboard", icon="📊", width="stretch")

with c2:
    st.markdown(
        """
<div class="ui-card" style="min-height: 175px;">
  <h3>🩺 Predicción individual</h3>
  <p>Ingresa los datos demográficos, clínicos y hábitos de un paciente para obtener su puntaje de riesgo, medidor y factores clave.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/03_prediccion_individual.py", label="Evaluar un paciente", icon="🩺", width="stretch")

with c3:
    st.markdown(
        """
<div class="ui-card" style="min-height: 175px;">
  <h3>📂 Predicción masiva</h3>
  <p>Descarga la plantilla CSV, carga cientos de registros clínicos en lote, visualiza la distribución de riesgo y exporta los resultados.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/04_prediccion_masiva.py", label="Cargar lote CSV", icon="📂", width="stretch")

st.info(
    "⚠️ **Aviso importante:** Este prototipo fue entrenado con `class_weight` para priorizar sensibilidad (F2-óptimo). "
    "La probabilidad estimada sobreestima el riesgo absoluto y debe interpretarse únicamente como puntaje relativo educativo, "
    "no como diagnóstico médico."
)

render_footer()
