"""Sistema de diseño, CSS global y componentes visuales reutilizables."""
import html
import streamlit as st
from core.model import PREVALENCE, THRESHOLD


def inject_css() -> None:
    """Inyecta tokens de estilo, tipografía tabular y componentes CSS."""
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

:root {
  --bg: #FAF8F5;
  --surface: #FFFFFF;
  --border: #E7E2DA;
  --text: #1E242B;
  --muted: #5F6875;
  --primary: #8B1E2B;
  --primary-dark: #5E111E;
  --primary-light: #FDF2F3;
  --ok: #1F7A4C;
  --warn: #B7791F;
  --danger: #A61B2B;
}

html, body, .stApp {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}

h1, h2, h3, .hero h1 {
  font-family: 'Plus Jakarta Sans', 'Inter', system-ui, sans-serif !important;
  letter-spacing: -0.02em;
  text-wrap: balance;
}

.block-container {
  max-width: 1220px;
  padding: 1.5rem 2.2rem 3.5rem;
}

/* Tabular numbers para métricas y porcentajes */
.tabular, [data-testid="stMetricValue"], .kpi-value, .gauge-pct, table {
  font-variant-numeric: tabular-nums;
}

/* Sidebar institucional oscuro */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #4A0E17 0%, #5E111E 55%, #3C0A12 100%) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

section[data-testid="stSidebar"] * {
  color: #F9F5F2 !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
  border-radius: 10px;
  margin: 0.15rem 0.5rem;
  padding: 0.45rem 0.75rem;
  transition-property: background-color, transform;
  transition-duration: 150ms;
  transition-timing-function: ease-out;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
  background-color: rgba(255, 255, 255, 0.12) !important;
}

section[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {
  background-color: rgba(255, 255, 255, 0.20) !important;
  font-weight: 700 !important;
}

section[data-testid="stSidebar"] hr {
  border-color: rgba(255, 255, 255, 0.16) !important;
}

/* Hero cardiológico */
.hero {
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #4A0E17 0%, #8B1E2B 58%, #B8323F 100%);
  border-radius: 20px;
  padding: 2.1rem 2.2rem;
  color: #FFFFFF;
  margin-bottom: 1.5rem;
  box-shadow: 0 10px 30px rgba(94, 17, 30, 0.18);
}

.hero::after {
  content: "";
  position: absolute;
  right: -60px;
  bottom: -90px;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
  pointer-events: none;
}

.hero-eyebrow {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #FBD5D8;
  margin-bottom: 0.55rem;
}

.hero h1 {
  color: #FFFFFF !important;
  font-size: clamp(1.65rem, 2.6vw, 2.35rem);
  font-weight: 800;
  line-height: 1.15;
  margin: 0 0 0.55rem 0;
}

.hero p {
  color: rgba(255, 245, 245, 0.90) !important;
  font-size: 0.98rem;
  line-height: 1.5;
  margin: 0;
  max-width: 760px;
}

.hero-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1.05rem;
}

.hero-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.22);
  color: #FFFFFF;
  border-radius: 999px;
  padding: 0.28rem 0.85rem;
  font-size: 0.78rem;
  font-weight: 600;
}

/* Cards de superficie */
.ui-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.35rem 1.45rem;
  box-shadow: 0 2px 8px rgba(30, 36, 43, 0.04), 0 8px 24px rgba(30, 36, 43, 0.04);
  margin-bottom: 1rem;
}

.ui-card-eyebrow {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: #1F7A4C;
  margin-bottom: 0.35rem;
}

.ui-card h3 {
  color: var(--primary);
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0 0 0.45rem 0;
}

.ui-card p {
  color: var(--muted);
  font-size: 0.92rem;
  line-height: 1.5;
  margin: 0;
}

/* KPI cards */
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: 3px solid var(--primary);
  border-radius: 14px;
  padding: 1rem 1.15rem;
  box-shadow: 0 2px 8px rgba(30, 36, 43, 0.04);
}

.kpi-label {
  font-size: 0.76rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
}

.kpi-value {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text);
  line-height: 1.2;
  margin: 0.2rem 0;
}

.kpi-sub {
  font-size: 0.78rem;
  color: var(--muted);
}

/* Formularios y botones */
div[data-testid="stForm"], section[data-testid="stForm"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  padding: 1.35rem 1.5rem !important;
  box-shadow: 0 2px 10px rgba(30, 36, 43, 0.04) !important;
}

div.stButton > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button {
  background: var(--primary) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.62rem 1.35rem !important;
  font-weight: 700 !important;
  transition-property: transform, background-color, box-shadow;
  transition-duration: 150ms;
  transition-timing-function: ease-out;
}

div.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
  background: var(--primary-dark) !important;
  box-shadow: 0 4px 14px rgba(139, 30, 43, 0.24) !important;
}

div.stButton > button:active,
div[data-testid="stFormSubmitButton"] > button:active {
  transform: scale(0.98);
}

/* Panel sticky de predicción */
.sticky-panel {
  position: sticky;
  top: 1.25rem;
}

.placeholder-box {
  background: var(--surface);
  border: 2px dashed #D9D2C7;
  border-radius: 18px;
  padding: 2.6rem 1.5rem;
  text-align: center;
  color: var(--muted);
}

/* Tarjeta de resultado */
.result-badge {
  display: inline-block;
  border-radius: 999px;
  padding: 0.25rem 0.9rem;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.badge-bajo { background: #E6F4EC; color: #166534; }
.badge-medio { background: #FEF3C7; color: #92400E; }
.badge-alto { background: #FDE8EA; color: #991B1B; }

.driver-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.48rem 0;
  border-bottom: 1px solid #F1EDE6;
  font-size: 0.88rem;
}

.driver-pill-up {
  background: #FDE8EA;
  color: #991B1B;
  border-radius: 999px;
  padding: 0.14rem 0.6rem;
  font-size: 0.74rem;
  font-weight: 700;
}

.driver-pill-down {
  background: #E6F4EC;
  color: #166534;
  border-radius: 999px;
  padding: 0.14rem 0.6rem;
  font-size: 0.74rem;
  font-weight: 700;
}

.sidebar-box {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  padding: 0.85rem 0.95rem;
  font-size: 0.82rem;
  line-height: 1.45;
  margin-top: 0.75rem;
}

.app-footer {
  text-align: center;
  color: var(--muted);
  font-size: 0.8rem;
  margin-top: 2.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

@media (max-width: 768px) {
  .block-container { padding: 1rem 1rem 2.5rem; }
  .hero { padding: 1.45rem 1.2rem; border-radius: 16px; }
  .sticky-panel { position: static; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    """Renderiza el bloque institucional y resumen del modelo en el sidebar."""
    with st.sidebar:
        st.markdown(
            f"""
<div style="padding: 0.25rem 0 0.5rem;">
  <div style="font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; opacity: 0.8;">
    Universidad del Cauca
  </div>
  <div style="font-size: 1.08rem; font-weight: 800; margin-top: 0.15rem;">
    🫀 Framingham CHD
  </div>
  <div style="font-size: 0.8rem; opacity: 0.85;">
    Inteligencia de Datos · Modelo v1
  </div>
</div>
<div class="sidebar-box">
  <div style="font-weight: 700; margin-bottom: 0.35rem;">Métricas verificadas (test)</div>
  <div class="tabular">• PR-AUC: <b>0.2689</b></div>
  <div class="tabular">• ROC-AUC: <b>0.6902</b></div>
  <div class="tabular">• Umbral F2: <b>{THRESHOLD:.2%}</b></div>
  <div class="tabular">• Prevalencia: <b>{PREVALENCE:.2%}</b></div>
</div>
<div class="sidebar-box" style="font-size: 0.76rem; opacity: 0.9;">
  <b>Nota de calibración:</b> Entrenado con <code>class_weight</code>; úsalo como puntaje relativo educativo, no diagnóstico médico.
</div>
            """,
            unsafe_allow_html=True,
        )


def render_hero(eyebrow: str, title: str, subtitle: str, chips: list[str] | None = None) -> None:
    """Renderiza el encabezado hero unificado."""
    chips_html = ""
    if chips:
        items = "".join(f'<span class="hero-chip">{html.escape(c)}</span>' for c in chips)
        chips_html = f'<div class="hero-chips">{items}</div>'
    st.markdown(
        f"""
<div class="hero">
  <div class="hero-eyebrow">{html.escape(eyebrow)}</div>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(subtitle)}</p>
  {chips_html}
</div>
        """,
        unsafe_allow_html=True,
    )


def render_gauge_svg(prob: float, nivel: str, msg: str, badge_cls: str, color_hex: str) -> None:
    """Renderiza un medidor semicircular SVG con umbral F2 y prevalencia."""
    pct = max(0.0, min(1.0, float(prob)))
    radius = 84
    circumference = 3.14159265 * radius
    dash_filled = circumference * pct
    thr_angle = 180.0 * (1.0 - THRESHOLD)
    import math

    rad = math.radians(thr_angle)
    cx, cy = 110, 102
    tx1 = cx + (radius - 9) * math.cos(rad)
    ty1 = cy - (radius - 9) * math.sin(rad)
    tx2 = cx + (radius + 9) * math.cos(rad)
    ty2 = cy - (radius + 9) * math.sin(rad)

    st.markdown(
        f"""
<div class="ui-card" style="text-align: center; padding: 1.4rem 1.2rem;">
  <div style="font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #5F6875;">
    Probabilidad estimada a 10 años
  </div>
  <svg viewBox="0 0 220 122" style="width: 100%; max-width: 260px; margin: 0.35rem auto 0;">
    <path d="M 26 102 A 84 84 0 0 1 194 102" fill="none" stroke="#EDE8DF" stroke-width="16" stroke-linecap="round"/>
    <path d="M 26 102 A 84 84 0 0 1 194 102" fill="none" stroke="{color_hex}" stroke-width="16"
          stroke-linecap="round" stroke-dasharray="{dash_filled:.2f} {circumference:.2f}"/>
    <line x1="{tx1:.1f}" y1="{ty1:.1f}" x2="{tx2:.1f}" y2="{ty2:.1f}" stroke="#1E242B" stroke-width="2.5" stroke-linecap="round"/>
    <text x="110" y="92" text-anchor="middle" class="gauge-pct" font-size="31" font-weight="800" fill="#1E242B">{pct:.1%}</text>
    <text x="26" y="118" text-anchor="middle" font-size="10" fill="#6B7280">0%</text>
    <text x="110" y="118" text-anchor="middle" font-size="10" fill="#1E242B" font-weight="600">Umbral {THRESHOLD:.1%}</text>
    <text x="194" y="118" text-anchor="middle" font-size="10" fill="#6B7280">100%</text>
  </svg>
  <div style="margin-top: 0.35rem;">
    <span class="result-badge badge-{badge_cls}">Riesgo {html.escape(nivel)}</span>
  </div>
  <p style="margin-top: 0.65rem; font-size: 0.88rem; color: #4B5563;">{html.escape(msg)}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Pie de página común."""
    st.markdown(
        """
<div class="app-footer">
  Herramienta educativa · NO reemplaza valoración médica · Cohorte Framingham (model_v1, PR-AUC 0.2689) ·
  <a href="https://github.com/adcamilox2000/framingham-risk-app" target="_blank">GitHub</a>
</div>
        """,
        unsafe_allow_html=True,
    )
