# Predictor de riesgo coronario — Framingham

Aplicación multipágina en **Streamlit** para el curso **Inteligencia de Datos (Unicauca)** basada en la cohorte Framingham y el pipeline `model_v1`.

> ⚠️ Herramienta EDUCATIVA. NO es un diagnóstico médico.

## Páginas incluidas

1. **Inicio (`pages/01_inicio.py`)**: Resumen ejecutivo, KPIs del modelo (`PR-AUC`, `ROC-AUC`, umbral F2, prevalencia) y accesos rápidos.
2. **Dashboard del modelo (`pages/02_dashboard.py`)**: Odds Ratios reales extraídos de `model_v1.joblib` y simulador interactivo de sensibilidad clínica.
3. **Predicción individual (`pages/03_prediccion_individual.py`)**: Formulario clínico, medidor gauge SVG semicircular y contribuciones reales (`x · β`) por paciente.
4. **Predicción masiva (`pages/04_prediccion_masiva.py`)**: Descarga de plantilla CSV, carga por lote, KPIs de cohorte, gráficas Altair y exportación de resultados.
5. **Acerca (`pages/05_acerca.py`)**: Documentación del pipeline `ClinicalFeatureEngineer`, diccionario de variables y nota de calibración.

## Modelo

- `LogisticRegression(class_weight)` — test PR-AUC **0.2689**, ROC-AUC **0.6902**, threshold F2-óptimo **0.4273**, prevalencia **15.25%**.
- Ver `artifacts/`: `model_v1.joblib` (pipeline completo) + `preprocessor_prepared_v1.joblib` (respaldo).
- Nota de calibración: entrenado con `class_weight`, sobreestima el riesgo absoluto. Interpretar como puntaje relativo.

## Correr local

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Deploy (Streamlit Community Cloud)

1. Push a GitHub (`main`).
2. En `share.streamlit.io` → `app.py` se autodespliega en cada push a `main`.
