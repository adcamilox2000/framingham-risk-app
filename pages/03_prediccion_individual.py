"""Página de predicción individual con gauge SVG y drivers dinámicos por paciente."""
import pandas as pd
import streamlit as st
from core.model import FEATURES, PREVALENCE, THRESHOLD, classify_risk, explain_patient, load_pipeline
from core.styles import render_footer, render_gauge_svg, render_hero

render_hero(
    eyebrow="Evaluación clínica individual",
    title="Predicción de Riesgo por Paciente",
    subtitle="Completa las variables demográficas, clínicas y de hábitos para calcular el puntaje de riesgo a 10 años.",
)

pipe = load_pipeline()
left, right = st.columns([1.45, 1], gap="large")

with left:
    with st.form("riesgo_individual"):
        st.subheader("1. Demografía")
        c1, c2 = st.columns(2)
        age = c1.number_input("Edad (años)", 20, 100, 45)
        male = c2.radio("Sexo", ["Mujer", "Hombre"], horizontal=True) == "Hombre"
        education = st.selectbox(
            "Educación (códigos ordinales del estudio Framingham: 1 menor a 4 mayor escolaridad)",
            [1, 2, 3, 4],
            format_func=lambda x: f"Nivel {x}",
        )

        st.subheader("2. Parámetros clínicos")
        c1, c2 = st.columns(2)
        sysBP = c1.number_input("Presión sistólica (mmHg)", 80, 300, 120)
        diaBP = c2.number_input("Presión diastólica (mmHg)", 40, 150, 80)
        totChol = c1.number_input("Colesterol total (mg/dL)", 100, 600, 190)
        bmi = c2.number_input("IMC (kg/m²)", 14.0, 60.0, 24.0, step=0.1)
        heartRate = c1.number_input("Frecuencia cardiaca (lpm)", 40, 160, 75)
        glucose = c2.number_input("Glucosa en ayunas (mg/dL)", 40.0, 500.0, 85.0, step=1.0)

        c1, c2 = st.columns(2)
        diabetes = c1.radio("Diabetes", ["No", "Sí"], horizontal=True) == "Sí"
        prevalentHyp = c2.radio("Hipertensión prevalente", ["No", "Sí"], horizontal=True) == "Sí"
        prevalentStroke = c1.radio("ACV previo", ["No", "Sí"], horizontal=True) == "Sí"
        BPMeds = c2.radio("Toma antihipertensivos", ["No", "Sí"], horizontal=True) == "Sí"

        st.subheader("3. Hábitos")
        cigsPerDay = st.number_input("Cigarrillos por día (0 = no fuma)", 0, 70, 0)

        submitted = st.form_submit_button("Calcular riesgo coronario")

with right:
    st.markdown('<div class="sticky-panel">', unsafe_allow_html=True)
    if submitted:
        if sysBP <= diaBP:
            st.warning("La presión sistólica normalmente es mayor que la diastólica. Verifica los valores ingresados.")

        row = pd.DataFrame(
            [{
                "male": int(male),
                "age": float(age),
                "education": float(education),
                "currentSmoker": int(cigsPerDay > 0),
                "cigsPerDay": float(cigsPerDay),
                "BPMeds": int(BPMeds),
                "prevalentStroke": int(prevalentStroke),
                "prevalentHyp": int(prevalentHyp),
                "diabetes": int(diabetes),
                "totChol": float(totChol),
                "sysBP": float(sysBP),
                "diaBP": float(diaBP),
                "BMI": float(bmi),
                "heartRate": float(heartRate),
                "glucose": float(glucose),
            }],
            columns=FEATURES,
        )

        prob = float(pipe.predict_proba(row)[0, 1])
        nivel, msg, badge_cls, color_hex = classify_risk(prob)
        render_gauge_svg(prob, nivel, msg, badge_cls, color_hex)

        ratio_prev = prob / PREVALENCE
        st.markdown(
            f"""
<div class="ui-card" style="padding: 1rem 1.2rem;">
  <div style="display:flex; justify-content:space-between; font-size:0.86rem; margin-bottom:0.5rem;">
    <span>Vs. prevalencia cohorte ({PREVALENCE:.2%})</span>
    <b class="tabular">{ratio_prev:.2f}×</b>
  </div>
  <div style="display:flex; justify-content:space-between; font-size:0.86rem;">
    <span>Presión de pulso calculada</span>
    <b class="tabular">{sysBP - diaBP} mmHg</b>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("**Principales factores en este paciente** *(contribución real en log-odds)*")
        exp_df = explain_patient(pipe, row).head(6)
        for _, item in exp_df.iterrows():
            pill_cls = "driver-pill-up" if item["contrib"] >= 0 else "driver-pill-down"
            sign = "+" if item["contrib"] >= 0 else ""
            st.markdown(
                f"""
<div class="driver-row">
  <span>{item['label']}</span>
  <span class="{pill_cls} tabular">{sign}{item['contrib']:.2f} ({item['direccion']})</span>
</div>
                """,
                unsafe_allow_html=True,
            )
        st.caption("Contribuciones individuales (x·β) calculadas directamente sobre el pipeline preprocesado.")
    else:
        st.markdown(
            """
<div class="placeholder-box">
  <div style="font-size:2.6rem;">🫀</div>
  <p style="font-weight:600; color:#1E242B; margin:0.5rem 0 0.25rem;">
    Completa el formulario y presiona <b>Calcular riesgo coronario</b>
  </p>
  <p style="font-size:0.85rem; margin:0;">
    Aquí verás el medidor de riesgo, comparación con el umbral F2 (42.73%) y los factores clave del paciente.
  </p>
</div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

render_footer()
