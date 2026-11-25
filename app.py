"""Entrypoint multipágina — Predictor de riesgo coronario Framingham (Unicauca)."""
import streamlit as st
from core.styles import inject_css, render_sidebar

st.set_page_config(
    page_title="Riesgo Framingham · Unicauca",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
render_sidebar()

nav = st.navigation(
    [
        st.Page("pages/01_inicio.py", title="Inicio", icon="🏠", default=True),
        st.Page("pages/02_dashboard.py", title="Dashboard del modelo", icon="📊"),
        st.Page("pages/03_prediccion_individual.py", title="Predicción individual", icon="🩺"),
        st.Page("pages/04_prediccion_masiva.py", title="Predicción masiva", icon="📂"),
        st.Page("pages/05_acerca.py", title="Acerca y metodología", icon="ℹ️"),
    ]
)
nav.run()
