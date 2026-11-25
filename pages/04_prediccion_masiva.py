"""Página de predicción masiva por lote CSV."""
import altair as alt
import pandas as pd
import streamlit as st
from core.model import FEATURE_META, THRESHOLD, load_pipeline, predict_batch, sample_csv_dataframe
from core.styles import render_footer, render_hero

render_hero(
    eyebrow="Carga por lote",
    title="Predicción Masiva para Múltiples Pacientes",
    subtitle="Sube un archivo CSV con las 15 variables clínicas de Framingham para estimar el riesgo en lote y exportar resultados.",
)

pipe = load_pipeline()

st.markdown(
    """
<div class="ui-card">
  <div class="ui-card-eyebrow">Paso 1 · Preparar archivo</div>
  <h3>Suba su archivo CSV</h3>
  <p>El pipeline procesará automáticamente cada fila, imputará faltantes numéricos si existen y clasificará el nivel de riesgo.</p>
</div>
    """,
    unsafe_allow_html=True,
)

c_dl, c_exp = st.columns([1, 2], gap="medium")
with c_dl:
    sample_df = sample_csv_dataframe()
    st.download_button(
        label="⬇️ Descargar plantilla CSV (5 ejemplos)",
        data=sample_df.to_csv(index=False).encode("utf-8"),
        file_name="plantilla_framingham.csv",
        mime="text/csv",
        width="stretch",
    )

with c_exp:
    with st.expander("Columnas requeridas en el CSV (15 variables)"):
        meta_df = pd.DataFrame(FEATURE_META, columns=["Columna", "Descripción", "Formato esperado"])
        st.dataframe(meta_df, width="stretch", hide_index=True)

uploaded = st.file_uploader("Seleccione un archivo CSV", type=["csv"])

if uploaded is not None:
    try:
        raw_df = pd.read_csv(uploaded)
        if raw_df.empty:
            st.warning("El archivo CSV está vacío. Usa la plantilla de ejemplo para probar.")
        else:
            result_df, warnings_list = predict_batch(pipe, raw_df)
            for w in warnings_list[:5]:
                st.warning(w)

            total = len(result_df)
            n_alto = int(result_df["supera_umbral_f2"].sum())
            pct_alto = (n_alto / total) * 100.0
            mean_p = float(result_df["prob_chd_10y"].mean())
            max_p = float(result_df["prob_chd_10y"].max())

            k1, k2, k3, k4 = st.columns(4)
            kpis = [
                (k1, "Pacientes evaluados", f"{total:,}", "Registros procesados"),
                (k2, "Superan umbral F2", f"{n_alto:,} ({pct_alto:.1f}%)", f"Probabilidad ≥ {THRESHOLD:.2%}"),
                (k3, "Probabilidad media", f"{mean_p:.1%}", "Promedio del lote"),
                (k4, "Probabilidad máxima", f"{max_p:.1%}", "Caso de mayor puntaje"),
            ]
            for col, label, val, sub in kpis:
                with col:
                    st.markdown(
                        f"""
<div class="kpi-card">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{val}</div>
  <div class="kpi-sub">{sub}</div>
</div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
            g1, g2 = st.columns(2, gap="large")

            with g1:
                cat_counts = (
                    result_df["categoria_riesgo"]
                    .value_counts()
                    .reindex(["BAJO", "MODERADO", "ELEVADO", "ALTO"], fill_value=0)
                    .reset_index()
                )
                cat_counts.columns = ["Categoría", "Pacientes"]
                bar_chart = (
                    alt.Chart(cat_counts)
                    .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                    .encode(
                        x=alt.X("Categoría:N", sort=["BAJO", "MODERADO", "ELEVADO", "ALTO"], title=None),
                        y=alt.Y("Pacientes:Q", title="Cantidad de pacientes"),
                        color=alt.Color(
                            "Categoría:N",
                            scale=alt.Scale(
                                domain=["BAJO", "MODERADO", "ELEVADO", "ALTO"],
                                range=["#1F7A4C", "#D97706", "#EA580C", "#A61B2B"],
                            ),
                            legend=None,
                        ),
                        tooltip=["Categoría", "Pacientes"],
                    )
                    .properties(title="Distribución por categoría de riesgo", height=290)
                    .configure_view(strokeWidth=0)
                )
                st.altair_chart(bar_chart, width="stretch")

            with g2:
                hist = (
                    alt.Chart(result_df)
                    .mark_bar(color="#8B1E2B", opacity=0.85, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                    .encode(
                        x=alt.X("prob_chd_10y:Q", bin=alt.Bin(maxbins=20), title="Probabilidad estimada", axis=alt.Axis(format="%")),
                        y=alt.Y("count()", title="Frecuencia"),
                        tooltip=[alt.Tooltip("count()", title="Pacientes")],
                    )
                )
                rule = (
                    alt.Chart(pd.DataFrame({"x": [THRESHOLD]}))
                    .mark_rule(color="#1E242B", strokeDash=[5, 4], strokeWidth=2)
                    .encode(x="x:Q")
                )
                st.altair_chart(
                    (hist + rule)
                    .properties(title="Histograma de probabilidades (línea = umbral 42.73%)", height=290)
                    .configure_view(strokeWidth=0),
                    width="stretch",
                )

            cats_filter = st.multiselect(
                "Filtrar tabla por categoría de riesgo",
                ["BAJO", "MODERADO", "ELEVADO", "ALTO"],
                default=["BAJO", "MODERADO", "ELEVADO", "ALTO"],
            )
            filtered = result_df[result_df["categoria_riesgo"].isin(cats_filter)]
            st.dataframe(filtered, width="stretch", hide_index=True)

            st.download_button(
                label="📥 Descargar resultados completos (.csv)",
                data=result_df.to_csv(index=False).encode("utf-8"),
                file_name="framingham_predicciones.csv",
                mime="text/csv",
            )
    except ValueError as err:
        st.error(f"Error de formato en el CSV: {err}")
    except Exception as err:
        st.error(f"No fue posible procesar el archivo CSV: {err}")

render_footer()
