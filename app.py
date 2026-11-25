"""Predictor de riesgo de CHD a 10 años — cohorte Framingham.

Herramienta EDUCATIVA para el curso Inteligencia de Datos (Unicauca).
NO es un diagnóstico médico: no reemplaza la valoración de un profesional.
Modelo: LogisticRegression class_weight (model_v1, test PR-AUC 0.2689).
"""
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path

ART = Path(__file__).parent / "artifacts"
THRESHOLD = 0.4273  # F2-optimal en validación (cell 4.9)
PREVALENCE = 0.1525  # tasa de eventos CHD en la cohorte

FEATURES = ["male", "age", "education", "currentSmoker", "cigsPerDay",
            "BPMeds", "prevalentStroke", "prevalentHyp", "diabetes",
            "totChol", "sysBP", "diaBP", "BMI", "heartRate", "glucose"]


@st.cache_resource
def load_pipeline():
    """Carga model_v1.joblib (Pipeline completo) o compone preprocessor+modelo."""
    import __main__
    from features import ClinicalFeatureEngineer
    __main__.ClinicalFeatureEngineer = ClinicalFeatureEngineer  # el pickle la busca en __main__
    model = joblib.load(ART / "model_v1.joblib")
    if hasattr(model, "predict_proba") and hasattr(model, "named_steps"):
        return model
    pre = joblib.load(ART / "preprocessor_prepared_v1.joblib")
    from sklearn.pipeline import Pipeline
    return Pipeline([("preprocessor", pre), ("model", model)])


st.set_page_config(page_title="Riesgo Framingham", page_icon="🫀")
st.title("🫀 Predictor de riesgo coronario (Framingham)")
st.warning("Herramienta educativa del curso Inteligencia de Datos. "
          "NO es un diagnóstico médico: ante cualquier duda consulta a un profesional.")

pipe = load_pipeline()

st.subheader("Hábitos")
smoker = st.radio("¿Fumas actualmente?", ["No", "Sí"], horizontal=True) == "Sí"

with st.form("riesgo"):
    st.subheader("Demografía")
    c1, c2 = st.columns(2)
    age = c1.number_input("Edad (años)", 20, 100, 45)
    male = c2.radio("Sexo", ["Mujer", "Hombre"], horizontal=True) == "Hombre"
    education = st.selectbox("Educación", [1, 2, 3, 4],
                             format_func=lambda x: f"Nivel {x}")

    st.subheader("Clínica")
    c1, c2 = st.columns(2)
    sysBP = c1.number_input("Presión sistólica (mmHg)", 80, 300, 120)
    diaBP = c2.number_input("Presión diastólica (mmHg)", 40, 150, 80)
    totChol = c1.number_input("Colesterol total (mg/dL)", 100, 600, 190)
    bmi = c2.number_input("IMC (kg/m²)", 14.0, 60.0, 24.0)
    heartRate = c2.number_input("Frecuencia cardiaca (lpm)", 40, 160, 75)
    glucose = st.number_input("Glucosa en ayunas (mg/dL)", 40.0, 500.0, 85.0)
    c1, c2 = st.columns(2)
    diabetes = c1.radio("Diabetes", ["No", "Sí"], horizontal=True) == "Sí"
    prevalentHyp = c2.radio("Hipertensión prevalente", ["No", "Sí"], horizontal=True) == "Sí"
    prevalentStroke = c1.radio("ACV previo", ["No", "Sí"], horizontal=True) == "Sí"
    BPMeds = c2.radio("Toma antihipertensivos", ["No", "Sí"], horizontal=True) == "Sí"

    st.subheader("Hábito de fumar")
    cigsPerDay = st.number_input("Cigarrillos por día", 0, 70, 10) if smoker else 0

    go = st.form_submit_button("Calcular riesgo")

if go:
    row = pd.DataFrame([{
        "male": int(male), "age": float(age), "education": float(education),
        "currentSmoker": int(smoker), "cigsPerDay": float(cigsPerDay),
        "BPMeds": int(BPMeds), "prevalentStroke": int(prevalentStroke),
        "prevalentHyp": int(prevalentHyp), "diabetes": int(diabetes),
        "totChol": float(totChol), "sysBP": float(sysBP),
        "diaBP": float(diaBP), "BMI": float(bmi),
        "heartRate": float(heartRate), "glucose": float(glucose),
    }], columns=FEATURES)
    p = float(pipe.predict_proba(row)[0, 1])

    st.metric("Probabilidad estimada a 10 años", f"{p:.1%}")
    st.progress(min(max(p, 0.0), 1.0))

    if p < PREVALENCE:
        st.info(f"Por debajo de la prevalencia de la cohorte ({PREVALENCE:.2%}).")
    elif p < 0.30:
        st.info("Riesgo moderado frente a la cohorte.")
    elif p < THRESHOLD:
        st.warning("Riesgo elevado, aún bajo el umbral de alto riesgo del modelo.")
    if p >= THRESHOLD:
        st.error(f"Riesgo alto según el umbral F2-óptimo del modelo ({THRESHOLD:.2%}). "
                 "Enfoque educativo: revisa hábitos y consulta a un profesional.")
    else:
        st.success("Por debajo del umbral de alto riesgo del modelo.")

    st.caption("Nota de calibración: el modelo se entrenó con class_weight, "
               "así que sobreestima el riesgo absoluto. Úsalo como puntaje "
               "relativo, no como riesgo calibrado. Referencia (no-skill): 15.25%.")
