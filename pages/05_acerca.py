"""Página informativa — Metodología, ingeniería de variables y créditos."""
import pandas as pd
import streamlit as st
from core.model import FEATURE_META, PREVALENCE, THRESHOLD
from core.styles import render_footer, render_hero

render_hero(
    eyebrow="Documentación técnica",
    title="Acerca del Modelo y Metodología",
    subtitle="Arquitectura del pipeline clínico, transformación de variables y consideraciones de calibración.",
)

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown(
        f"""
<div class="ui-card">
  <div class="ui-card-eyebrow">Pipeline de ML</div>
  <h3>ClinicalFeatureEngineer + LogisticRegression</h3>
  <p>
    El artefacto <code>model_v1.joblib</code> encapsula el preprocesamiento clínico y un clasificador
    <code>LogisticRegression(class_weight)</code> ajustado para maximizar la detección de casos positivos en un
    escenario desbalanceado (prevalencia base <b>{PREVALENCE:.2%}</b>).
  </p>
  <ul style="margin-top: 0.7rem; color: #4B5563; font-size: 0.9rem; line-height: 1.55;">
    <li><b>pulse_pressure:</b> diferencia <code>sysBP - diaBP</code>.</li>
    <li><b>glucose_log &amp; glucose_missing:</b> transformación logarítmica e indicador de ausencia.</li>
    <li><b>cigsPerDay:</b> reparación según <code>currentSmoker</code> con mediana aprendida en entrenamiento.</li>
    <li><b>Umbral F2-óptimo ({THRESHOLD:.2%}):</b> prioriza recall frente a falsos negativos.</li>
  </ul>
</div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
<div class="ui-card">
  <div class="ui-card-eyebrow">Calibración y ética</div>
  <h3>Interpretación responsable del puntaje</h3>
  <p>
    Al entrenar con ponderación de clases (<code>class_weight</code>), las probabilidades predichas se desplazan
    hacia arriba respecto al riesgo absoluto poblacional.
  </p>
  <ul style="margin-top: 0.7rem; color: #4B5563; font-size: 0.9rem; line-height: 1.55;">
    <li>Úsalo como <b>puntaje relativo de riesgo</b> para fines académicos y demostrativos.</li>
    <li><b>No reemplaza</b> guías clínicas validadas ni el criterio de un médico.</li>
    <li>Desarrollado para el curso <b>Inteligencia de Datos — Universidad del Cauca</b>.</li>
  </ul>
</div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("### Diccionario de las 15 variables de entrada")
st.dataframe(
    pd.DataFrame(FEATURE_META, columns=["Variable", "Nombre clínico", "Tipo / Rango"]),
    width="stretch",
    hide_index=True,
)

render_footer()
