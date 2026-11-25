# Predictor de riesgo coronario — Framingham

Mini app Streamlit (estilo app de desertores del profe): formulario con las
13 variables del modelo → probabilidad de CHD a 10 años con `model_v1`.

> ⚠️ Herramienta EDUCATIVA del curso Inteligencia de Datos (Unicauca).
> NO es un diagnóstico médico.

## Modelo

- `LogisticRegression(class_weight)` C=0.0333 — test PR-AUC **0.2689**,
  ROC-AUC **0.6902**, threshold F2-óptimo **0.4273**, prevalencia **15.25%**.
- Ver `artifacts/`: `model_v1.joblib` (pipeline completo) +
  `preprocessor_prepared_v1.joblib` (respaldo).
- Nota de calibración: entrenado con `class_weight`, sobreestima el riesgo
  absoluto. Interpretar como puntaje relativo, no riesgo calibrado.

## Correr local

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Deploy (Streamlit Community Cloud, gratis)

1. Push a GitHub (repo público).
2. En share.streamlit.io → New app → repo, branch `main`, `app.py` → Deploy.
3. Rollback: revertir el commit / borrar la app en Cloud.
