"""Predictor de riesgo de CHD a 10 años — cohorte Framingham.

Herramienta EDUCATIVA para el curso Inteligencia de Datos (Unicauca).
NO es un diagnóstico médico: no reemplaza la valoración de un profesional.
Modelo: LogisticRegression class_weight (model_v1, test PR-AUC 0.2689).
"""
import joblib
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


st.set_page_config(page_title="Riesgo Framingham", page_icon="🫀", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, .stApp, .stApp p, .stApp label, .stApp input, .stApp button,
.stApp div, [data-testid="stSidebar"] * { font-family: 'Inter', system-ui, sans-serif !important; }
.block-container { max-width: 1150px; padding: 1rem 2rem 3rem; }
.hero { background: linear-gradient(135deg, #7f1d1d 0%, #c0392b 55%, #e74c3c 100%);
    border-radius: 0 0 20px 20px; padding: 2.2rem 2rem; color: white; margin: -1rem -2rem 1.5rem; }
.hero h1 { color: white !important; font-weight: 800; letter-spacing: -0.5px; margin: 0; }
.hero p { color: #ffe9e6 !important; margin: .3rem 0 0; }
.hero .chip { display: inline-block; background: rgba(255,255,255,.18); color: white;
    border-radius: 999px; padding: .25rem .9rem; font-size: .8rem; margin-top: .8rem; }
div[data-testid="stForm"], section[data-testid="stForm"] { border: 1px solid #e5e7eb;
    border-radius: 16px; padding: 1.2rem 1.4rem; box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    background: white; }
div.stButton > button, div[data-testid="stBaseButton-secondary"] > button {
    background: #c0392b; color: white; border: none; border-radius: 14px;
    padding: .65rem 1.6rem; font-weight: 700; width: 100%; }
div.stButton > button:hover, div[data-testid="stBaseButton-secondary"] > button:hover {
    background: #a93226; color: white; }
.sticky-panel { position: sticky; top: 1.2rem; }
.placeholder-box { border: 2px dashed #e5e7eb; border-radius: 18px; padding: 2.5rem 1.5rem;
    text-align: center; color: #9ca3af; }
.result-card { border-radius: 18px; padding: 1.4rem; text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin: 1rem 0; }
.result-card .big { font-size: 3.2rem; font-weight: 800; line-height: 1.1; }
.bajo { background: linear-gradient(180deg, #e8f5e9, #c8e6c9); color: #1b5e20; }
.medio { background: linear-gradient(180deg, #fff8e1, #ffecb3); color: #7a5c00; }
.alto { background: linear-gradient(180deg, #fdecea, #f5c6c0); color: #8e1b1b; }
.bar-track { background: #eee; border-radius: 999px; height: 14px; position: relative; margin: .8rem 0 .2rem; }
.bar-fill { height: 14px; border-radius: 999px; }
.bar-thr { position: absolute; top: -4px; bottom: -4px; width: 2px; background: #333; }
.driver { display: flex; justify-content: space-between; align-items: center;
    padding: .35rem 0; border-bottom: 1px solid #f0f0f0; font-size: .9rem; }
.driver .tag { font-size: .72rem; border-radius: 999px; padding: .1rem .6rem; font-weight: 700; }
.tag-you { background: #fdecea; color: #8e1b1b; }
.tag-or { background: #f3f4f6; color: #374151; }
.footer { text-align: center; color: #9ca3af; font-size: .8rem; margin-top: 2rem; }
@media (max-width: 768px) {
    .hero { padding: 1.4rem 1rem; }
    .block-container { padding: 1rem; }
    .sticky-panel { position: static; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🫀 Predictor de riesgo coronario a 10 años</h1>
<p>Cohorte Framingham · Curso Inteligencia de Datos — Unicauca</p>
<div class="chip">🫀 Herramienta educativa — no es diagnóstico médico</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("ℹ️ Cómo funciona")
    st.markdown("Tus **13 variables** entran al modelo LogReg `model_v1` y sale la **probabilidad de CHD a 10 años**.")
    st.markdown("**Métricas del modelo**")
    st.markdown("- PR-AUC test: **0.2689**\n- ROC-AUC test: **0.6902**\n- Umbral F2-óptimo: **42.73%**\n- Prevalencia cohorte: **15.25%**")
    st.caption("Nota de calibración: entrenado con class_weight, sobreestima el riesgo absoluto. Úsalo como puntaje relativo, no como riesgo calibrado.")

pipe = load_pipeline()

left, right = st.columns([1.5, 1], gap="large")

with left:
    with st.form("riesgo"):
        st.subheader("Demografía")
        c1, c2 = st.columns(2)
        age = c1.number_input("Edad (años)", 20, 100, 45)
        male = c2.radio("Sexo", ["Mujer", "Hombre"], horizontal=True) == "Hombre"
        education = st.selectbox(
            "Educación (códigos ordinales del estudio: 1 menor a 4 mayor escolaridad)",
            [1, 2, 3, 4],
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

        st.subheader("Hábitos")
        cigsPerDay = st.number_input("Cigarrillos por día (0 = no fuma)", 0, 70, 0)

        go = st.form_submit_button("Calcular riesgo")

with right:
    st.markdown('<div class="sticky-panel">', unsafe_allow_html=True)
    if go:
        row = pd.DataFrame([{
            "male": int(male), "age": float(age), "education": float(education),
            "currentSmoker": int(cigsPerDay > 0), "cigsPerDay": float(cigsPerDay),
            "BPMeds": int(BPMeds), "prevalentStroke": int(prevalentStroke),
            "prevalentHyp": int(prevalentHyp), "diabetes": int(diabetes),
            "totChol": float(totChol), "sysBP": float(sysBP),
            "diaBP": float(diaBP), "BMI": float(bmi),
            "heartRate": float(heartRate), "glucose": float(glucose),
        }], columns=FEATURES)
        p = float(pipe.predict_proba(row)[0, 1])

        if p < THRESHOLD:
            nivel, msg, cls, fill = (
                ("BAJO", "Por debajo de la prevalencia de la cohorte (15.25%).", "bajo", "#43a047")
                if p < PREVALENCE else
                ("MODERADO", "Riesgo moderado frente a la cohorte.", "medio", "#f9a825") if p < 0.30 else
                ("ELEVADO", "Riesgo elevado, aún bajo el umbral de alto riesgo.", "medio", "#f9a825"))
        else:
            nivel, msg, cls, fill = ("ALTO",
                "Riesgo alto según el umbral F2-óptimo (42.73%). Revisa hábitos y consulta a un profesional.",
                "alto", "#c0392b")
        st.markdown(
            f'<div class="result-card {cls}"><div>Probabilidad estimada a 10 años</div>'
            f'<div class="big">{p:.1%}</div><div><b>Riesgo {nivel}</b> · {msg}</div></div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{p*100:.1f}%;background:{fill};"></div>'
            f'<div class="bar-thr" style="left:{THRESHOLD*100:.1f}%;" title="Umbral 42.73%"></div></div>'
            f'<div style="display:flex;justify-content:space-between;font-size:.75rem;color:#666;">'
            f'<span>0%</span><span>Umbral 42.73%</span><span>100%</span></div>',
            unsafe_allow_html=True)

        st.markdown("**Qué sube tu riesgo** *(odds ratio del modelo v1, orientativo)*")
        drivers = [
            ("Edad", 1.74, age >= 55),
            ("Sexo hombre", 1.37, bool(male)),
            ("Presión sistólica", 1.29, sysBP >= 130),
            ("Cigarrillos/día", 1.29, cigsPerDay > 0),
            ("Glucosa", 1.10, glucose >= 100),
        ]
        for name, or_, applies in drivers:
            tag = '<span class="tag tag-you">aplica a ti</span>' if applies else '<span class="tag tag-or">OR ' + f"{or_:.2f}</span>"
            st.markdown(f'<div class="driver"><span>{name}</span>{tag}</div>', unsafe_allow_html=True)
        st.caption("Pesos (odds ratio) del modelo v1; orientativo, no causal.")
    else:
        st.markdown("""
        <div class="placeholder-box">
        <div style="font-size:2.5rem;">🫀</div>
        <p>Completa el formulario y presiona <b>Calcular riesgo</b></p>
        <p style="font-size:.85rem;">El resultado aparece aquí</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="footer">
Herramienta educativa · NO reemplaza valoración médica · Modelo v1 (PR-AUC 0.2689) ·
<a href="https://github.com/adcamilox2000/framingham-risk-app">GitHub</a>
</div>
""", unsafe_allow_html=True)
