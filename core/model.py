"""Carga del modelo Framingham, inferencia individual/lote y explicabilidad."""
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
import streamlit as st

ART = Path(__file__).resolve().parent.parent / "artifacts"
THRESHOLD = 0.4273   # Umbral F2-óptimo en validación
PREVALENCE = 0.1525  # Prevalencia de CHD a 10 años en la cohorte

FEATURES = [
    "male", "age", "education", "currentSmoker", "cigsPerDay",
    "BPMeds", "prevalentStroke", "prevalentHyp", "diabetes",
    "totChol", "sysBP", "diaBP", "BMI", "heartRate", "glucose",
]

FEATURE_META = [
    ("male", "Sexo masculino", "Binaria (0 = Mujer, 1 = Hombre)"),
    ("age", "Edad", "Numérica (años, ej. 20–100)"),
    ("education", "Nivel educativo", "Ordinal del estudio (1 a 4)"),
    ("currentSmoker", "Fumador actual", "Binaria (0 = No, 1 = Sí)"),
    ("cigsPerDay", "Cigarrillos por día", "Numérica (0 si no fuma)"),
    ("BPMeds", "Toma antihipertensivos", "Binaria (0 = No, 1 = Sí)"),
    ("prevalentStroke", "ACV previo", "Binaria (0 = No, 1 = Sí)"),
    ("prevalentHyp", "Hipertensión prevalente", "Binaria (0 = No, 1 = Sí)"),
    ("diabetes", "Diabetes", "Binaria (0 = No, 1 = Sí)"),
    ("totChol", "Colesterol total", "Numérica (mg/dL)"),
    ("sysBP", "Presión sistólica", "Numérica (mmHg)"),
    ("diaBP", "Presión diastólica", "Numérica (mmHg)"),
    ("BMI", "Índice de masa corporal", "Numérica (kg/m²)"),
    ("heartRate", "Frecuencia cardiaca", "Numérica (lpm)"),
    ("glucose", "Glucosa en ayunas", "Numérica (mg/dL)"),
]

TRANSFORMED_LABELS = {
    "age": "Edad",
    "male": "Sexo masculino",
    "cigsPerDay": "Cigarrillos / día",
    "sysBP": "Presión sistólica",
    "prevalentHyp": "Hipertensión prevalente",
    "BPMeds": "Uso de antihipertensivos",
    "diabetes": "Diabetes",
    "prevalentStroke": "ACV previo",
    "totChol": "Colesterol total",
    "glucose_log": "Glucosa (log)",
    "BMI": "Índice de masa corporal",
    "heartRate": "Frecuencia cardiaca",
    "education_2.0": "Educación nivel 2 vs 1",
    "education_3.0": "Educación nivel 3 vs 1",
    "education_4.0": "Educación nivel 4 vs 1",
}


@st.cache_resource
def load_pipeline():
    """Carga model_v1.joblib inyectando ClinicalFeatureEngineer en __main__."""
    import __main__
    from features import ClinicalFeatureEngineer

    __main__.ClinicalFeatureEngineer = ClinicalFeatureEngineer
    model = joblib.load(ART / "model_v1.joblib")
    if hasattr(model, "predict_proba") and hasattr(model, "named_steps"):
        return model
    pre = joblib.load(ART / "preprocessor_prepared_v1.joblib")
    from sklearn.pipeline import Pipeline

    return Pipeline([("prep", pre), ("clf", model)])


def classify_risk(prob: float) -> tuple[str, str, str, str]:
    """Clasifica la probabilidad en categoría clínica relativa."""
    if prob < PREVALENCE:
        return (
            "BAJO",
            "Por debajo de la prevalencia de la cohorte (15.25%).",
            "bajo",
            "#1F7A4C",
        )
    if prob < 0.30:
        return (
            "MODERADO",
            "Riesgo moderado frente a la cohorte Framingham.",
            "medio",
            "#B7791F",
        )
    if prob < THRESHOLD:
        return (
            "ELEVADO",
            "Riesgo elevado, aún debajo del umbral F2-óptimo (42.73%).",
            "medio",
            "#D97706",
        )
    return (
        "ALTO",
        "Supera el umbral F2-óptimo (42.73%). Revisa hábitos y consulta a un profesional.",
        "alto",
        "#A61B2B",
    )


def _extract_prep_and_clf(pipe):
    prep = pipe.named_steps.get("prep") or pipe.named_steps.get("preprocessor")
    clf = pipe.named_steps.get("clf") or pipe.named_steps.get("model")
    return prep, clf


def get_model_drivers(pipe) -> pd.DataFrame:
    """Extrae coeficientes estandarizados y Odds Ratios reales del modelo."""
    prep, clf = _extract_prep_and_clf(pipe)
    names = list(prep.get_feature_names_out())
    coefs = clf.coef_[0]
    rows = []
    for name, coef in zip(names, coefs):
        rows.append({
            "feature": name,
            "label": TRANSFORMED_LABELS.get(name, name),
            "coef": float(coef),
            "abs_coef": abs(float(coef)),
            "odds_ratio": float(np.exp(coef)),
            "efecto": "Aumenta riesgo" if coef >= 0 else "Reduce riesgo",
        })
    return pd.DataFrame(rows).sort_values("abs_coef", ascending=False).reset_index(drop=True)


def explain_patient(pipe, row_df: pd.DataFrame) -> pd.DataFrame:
    """Calcula la contribución real en log-odds (x_i * beta_i) para un paciente."""
    prep, clf = _extract_prep_and_clf(pipe)
    names = list(prep.get_feature_names_out())
    X_t = np.asarray(prep.transform(row_df), dtype=float)[0]
    coefs = clf.coef_[0]
    rows = []
    for name, val, coef in zip(names, X_t, coefs):
        contrib = float(val * coef)
        rows.append({
            "feature": name,
            "label": TRANSFORMED_LABELS.get(name, name),
            "contrib": contrib,
            "abs_contrib": abs(contrib),
            "odds_ratio": float(np.exp(coef)),
            "direccion": "Sube el riesgo" if contrib >= 0 else "Baja el riesgo",
        })
    return pd.DataFrame(rows).sort_values("abs_contrib", ascending=False).reset_index(drop=True)


def sample_csv_dataframe() -> pd.DataFrame:
    """Retorna 5 perfiles clínicos válidos como plantilla descargable."""
    return pd.DataFrame([
        {
            "male": 0, "age": 38, "education": 3, "currentSmoker": 0, "cigsPerDay": 0,
            "BPMeds": 0, "prevalentStroke": 0, "prevalentHyp": 0, "diabetes": 0,
            "totChol": 175, "sysBP": 112, "diaBP": 72, "BMI": 22.4, "heartRate": 68, "glucose": 82,
        },
        {
            "male": 1, "age": 49, "education": 2, "currentSmoker": 1, "cigsPerDay": 10,
            "BPMeds": 0, "prevalentStroke": 0, "prevalentHyp": 0, "diabetes": 0,
            "totChol": 215, "sysBP": 128, "diaBP": 82, "BMI": 26.8, "heartRate": 76, "glucose": 94,
        },
        {
            "male": 1, "age": 61, "education": 1, "currentSmoker": 1, "cigsPerDay": 20,
            "BPMeds": 1, "prevalentStroke": 0, "prevalentHyp": 1, "diabetes": 1,
            "totChol": 268, "sysBP": 158, "diaBP": 96, "BMI": 31.2, "heartRate": 88, "glucose": 142,
        },
        {
            "male": 0, "age": 56, "education": 2, "currentSmoker": 0, "cigsPerDay": 0,
            "BPMeds": 1, "prevalentStroke": 0, "prevalentHyp": 1, "diabetes": 0,
            "totChol": 238, "sysBP": 144, "diaBP": 88, "BMI": 27.9, "heartRate": 74, "glucose": 99,
        },
        {
            "male": 1, "age": 44, "education": 4, "currentSmoker": 0, "cigsPerDay": 0,
            "BPMeds": 0, "prevalentStroke": 0, "prevalentHyp": 0, "diabetes": 0,
            "totChol": 192, "sysBP": 118, "diaBP": 76, "BMI": 24.5, "heartRate": 70, "glucose": 86,
        },
    ], columns=FEATURES)


def predict_batch(pipe, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Valida columnas requeridas y genera predicciones por lote."""
    missing = [col for col in FEATURES if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(missing)}")

    work = df.copy()
    warnings_list: list[str] = []
    for col in FEATURES:
        converted = pd.to_numeric(work[col], errors="coerce").astype("float64")
        na_count = int(converted.isna().sum())
        if na_count > 0:
            warnings_list.append(f"`{col}` tiene {na_count} valor(es) faltante(s) o no numérico(s) (el pipeline los imputará).")
        work[col] = converted

    probs = pipe.predict_proba(work[FEATURES])[:, 1]
    out = df.copy()
    out["prob_chd_10y"] = np.round(probs, 4)
    out["prob_pct"] = np.round(probs * 100.0, 2)
    out["categoria_riesgo"] = [classify_risk(float(p))[0] for p in probs]
    out["supera_umbral_f2"] = probs >= THRESHOLD
    return out, warnings_list
