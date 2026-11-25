"""Dashboard del modelo — Coeficientes reales y simulador de sensibilidad."""
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from core.model import FEATURES, PREVALENCE, THRESHOLD, get_model_drivers, load_pipeline
from core.styles import render_footer, render_hero

render_hero(
    eyebrow="Analítica del modelo",
    title="Dashboard de Interpretabilidad y Sensibilidad",
    subtitle=(
        "Pesos reales extraídos de model_v1.joblib y simulación interactiva de curvas de riesgo "
        "evaluando el pipeline clínico en tiempo real."
    ),
)

pipe = load_pipeline()
drivers_df = get_model_drivers(pipe)

left, right = st.columns([1.15, 1], gap="large")

with left:
    st.markdown(
        """
<div class="ui-card">
  <div class="ui-card-eyebrow">Pesos del modelo v1</div>
  <h3>Odds Ratios por variable estandarizada</h3>
  <p>Valores mayores a 1.0 incrementan la probabilidad estimada de CHD a 10 años; menores a 1.0 la atenúan.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    chart_or = (
        alt.Chart(drivers_df)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            x=alt.X("odds_ratio:Q", title="Odds Ratio (exp(β))", scale=alt.Scale(zero=False)),
            y=alt.Y("label:N", sort="-x", title=None),
            color=alt.Color(
                "efecto:N",
                scale=alt.Scale(
                    domain=["Aumenta riesgo", "Reduce riesgo"],
                    range=["#A61B2B", "#1F7A4C"],
                ),
                legend=alt.Legend(orient="top", title=None),
            ),
            tooltip=[
                alt.Tooltip("label:N", title="Variable"),
                alt.Tooltip("odds_ratio:Q", title="Odds Ratio", format=".3f"),
                alt.Tooltip("coef:Q", title="Coeficiente β", format=".4f"),
            ],
        )
        .properties(height=420)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#EFECE6", labelFontSize=12, titleFontSize=12)
    )
    st.altair_chart(chart_or, width="stretch")

with right:
    st.markdown(
        """
<div class="ui-card">
  <div class="ui-card-eyebrow">Simulador clínico en vivo</div>
  <h3>Sensibilidad por Edad y Presión Sistólica</h3>
  <p>Ajusta un perfil base para observar cómo responde <code>model_v1</code> entre fumadores y no fumadores.</p>
</div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    sim_male = c1.radio("Sexo perfil base", ["Mujer", "Hombre"], horizontal=True) == "Hombre"
    sim_hyp = c2.radio("Hipertensión", ["No", "Sí"], horizontal=True) == "Sí"
    sim_sys = st.slider("Presión sistólica base (mmHg)", 95, 200, 128)
    sim_chol = st.slider("Colesterol total (mg/dL)", 130, 340, 210)

    ages = np.arange(30, 76, 2)
    rows_sim = []
    for smoker_flag, label_group in [(0, "No fumador (0 cig/día)"), (1, "Fumador (15 cig/día)")]:
        for a in ages:
            rows_sim.append({
                "male": int(sim_male),
                "age": float(a),
                "education": 2.0,
                "currentSmoker": smoker_flag,
                "cigsPerDay": 15.0 if smoker_flag else 0.0,
                "BPMeds": 0,
                "prevalentStroke": 0,
                "prevalentHyp": int(sim_hyp),
                "diabetes": 0,
                "totChol": float(sim_chol),
                "sysBP": float(sim_sys),
                "diaBP": 80.0,
                "BMI": 25.5,
                "heartRate": 74.0,
                "glucose": 88.0,
                "grupo": label_group,
            })
    sim_df = pd.DataFrame(rows_sim)
    sim_df["prob"] = pipe.predict_proba(sim_df[FEATURES])[:, 1]

    line_chart = (
        alt.Chart(sim_df)
        .mark_line(strokeWidth=3)
        .encode(
            x=alt.X("age:Q", title="Edad (años)"),
            y=alt.Y("prob:Q", title="Probabilidad estimada", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
            color=alt.Color(
                "grupo:N",
                scale=alt.Scale(range=["#1F7A4C", "#8B1E2B"]),
                legend=alt.Legend(orient="top", title=None),
            ),
            tooltip=[
                alt.Tooltip("age:Q", title="Edad"),
                alt.Tooltip("grupo:N", title="Perfil"),
                alt.Tooltip("prob:Q", title="Riesgo estimado", format=".1%"),
            ],
        )
    )
    thr_rule = (
        alt.Chart(pd.DataFrame({"y": [THRESHOLD], "label": ["Umbral F2 (42.7%)"]}))
        .mark_rule(strokeDash=[6, 4], color="#1E242B", strokeWidth=1.8)
        .encode(y="y:Q")
    )
    prev_rule = (
        alt.Chart(pd.DataFrame({"y": [PREVALENCE], "label": ["Prevalencia (15.3%)"]}))
        .mark_rule(strokeDash=[3, 3], color="#B7791F", strokeWidth=1.5)
        .encode(y="y:Q")
    )
    st.altair_chart(
        (line_chart + thr_rule + prev_rule)
        .properties(height=310)
        .configure_view(strokeWidth=0)
        .configure_axis(gridColor="#EFECE6"),
        width="stretch",
    )
    st.caption("Línea negra punteada: umbral F2-óptimo (42.73%). Línea ámbar: prevalencia cohorte (15.25%).")

render_footer()
