"""Copia exacta de ClinicalFeatureEngineer del notebook Phase 3 (cell 3.6).

Necesaria porque model_v1.joblib y preprocessor_prepared_v1.joblib se
serializaron con la clase definida en __main__ del notebook. Al inyectarla
en __main__ antes de joblib.load, el unpickle funciona y los parámetros
ajustados (ej. smoker_cigs_median_) vienen del pickle, no se re-entrenan.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class ClinicalFeatureEngineer(BaseEstimator, TransformerMixin):
    """Domain features for the Framingham data.

    fit():       learns the median cigsPerDay among current smokers (training data only).
    transform(): repairs cigsPerDay, adds pulse_pressure, glucose_log and glucose_missing.
    """

    @staticmethod
    def _to_float(X):
        # pandas nullable Int8 -> float64 so sklearn imputers see np.nan instead of pd.NA
        X = pd.DataFrame(X).copy()
        for c in X.columns:
            if pd.api.types.is_extension_array_dtype(X[c]):
                X[c] = X[c].astype("float64")
        return X

    def fit(self, X, y=None):
        X = self._to_float(X)
        smokers = X.loc[X["currentSmoker"] == 1, "cigsPerDay"]
        self.smoker_cigs_median_ = float(smokers.median())
        self.feature_names_in_ = np.array(X.columns, dtype=object)
        return self

    def transform(self, X):
        X = self._to_float(X)
        cig_na = X["cigsPerDay"].isna()
        X.loc[cig_na & (X["currentSmoker"] == 0), "cigsPerDay"] = 0.0
        X.loc[cig_na & (X["currentSmoker"] == 1), "cigsPerDay"] = self.smoker_cigs_median_
        X["pulse_pressure"] = X["sysBP"] - X["diaBP"]
        X["glucose_missing"] = X["glucose"].isna().astype("int8")
        X["glucose_log"] = np.log(X["glucose"])  # NaN stays NaN -> imputed downstream
        return X

    def get_feature_names_out(self, input_features=None):
        base = list(self.feature_names_in_) if input_features is None else list(input_features)
        return np.array(base + ["pulse_pressure", "glucose_missing", "glucose_log"], dtype=object)
