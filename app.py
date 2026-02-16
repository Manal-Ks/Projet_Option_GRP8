import ast
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Recrutement | Forvis Mazars",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# BRAND COLORS
# ============================================================

NAVY   = "#1A2B8A"
BLUE   = "#0099D8"
LIGHT  = "#F2F5FB"
GRAY   = "#6B7A8D"
WHITE  = "#FFFFFF"
GREEN  = "#22C55E"
ORANGE = "#F59E0B"
RED    = "#EF4444"

# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
    font-family: 'Sora', sans-serif;
    background-color: {LIGHT};
    color: {NAVY};
}}

/* Sidebar base */
[data-testid="stSidebar"] {{
    background-color: {NAVY} !important;
    border-right: 3px solid {BLUE};
}}

/* Force white text on ALL sidebar elements */
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
    color: {WHITE} !important;
    font-family: 'Sora', sans-serif !important;
}}

/* Slider value bubble */
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBarMax"],
[data-testid="stSidebar"] [data-testid="stSlider"] p {{
    color: rgba(255,255,255,0.6) !important;
}}

/* Slider track color */
[data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {{
    background: {BLUE} !important;
}}

/* Selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] {{
    background-color: rgba(255,255,255,0.10) !important;
    border-radius: 6px;
    border: 1px solid rgba(255,255,255,0.2) !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] div {{
    background-color: transparent !important;
    color: {WHITE} !important;
}}

/* Hide default Streamlit sidebar header/icon */
[data-testid="stSidebarHeader"] {{
    display: none !important;
}}

/* Metric cards */
[data-testid="stMetric"] {{
    background: {WHITE};
    border-radius: 10px;
    padding: 18px 22px !important;
    border-top: 4px solid {BLUE};
    box-shadow: 0 2px 12px rgba(26,43,138,0.08);
}}
[data-testid="stMetricLabel"] {{
    font-size: 0.72rem !important;
    color: {GRAY} !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600 !important;
}}
[data-testid="stMetricValue"] {{
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: {NAVY} !important;
    font-family: 'IBM Plex Mono', monospace !important;
}}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{
    background: {WHITE};
    border-radius: 10px;
    padding: 4px;
    box-shadow: 0 2px 10px rgba(26,43,138,0.07);
    gap: 4px;
}}
[data-testid="stTabs"] [data-baseweb="tab"] {{
    border-radius: 8px !important;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 10px 22px !important;
    color: {GRAY} !important;
}}
[data-testid="stTabs"] [aria-selected="true"] {{
    background: {NAVY} !important;
    color: {WHITE} !important;
}}

hr {{
    border: none;
    border-top: 1px solid #e0e7ef;
    margin: 16px 0;
}}

/* Sidebar section labels */
.sidebar-label {{
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: {BLUE} !important;
    font-weight: 700;
    margin: 20px 0 8px 0;
    display: block;
}}

/* Section title */
.section-title {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {GRAY};
    font-weight: 700;
    margin-bottom: 14px;
    padding-bottom: 8px;
    border-bottom: 2px solid {BLUE};
}}

/* Candidate card */
.cand-card {{
    background: {WHITE};
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 2px 10px rgba(26,43,138,0.07);
    margin-bottom: 10px;
    border-left: 4px solid {BLUE};
}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================

SCORE_KEYS   = ["score_skills", "score_experience", "score_education", "score_languages", "score_sector"]
SCORE_LABELS = ["Compétences", "Expérience", "Formation", "Langues", "Secteur"]
WEIGHT_KEYS  = ["skills", "experience", "education", "languages", "sector"]

# ============================================================
# HELPERS
# ============================================================

def score_pill(val: float) -> str:
    """Return a colored HTML pill based on the score value."""
    pct = int(round(val * 100))
    if val >= 0.70:
        css = "background:#DCFCE7; color:#15803D;"
    elif val >= 0.45:
        css = "background:#FEF3C7; color:#B45309;"
    else:
        css = "background:#FEE2E2; color:#B91C1C;"
    return (
        f'<span style="{css} font-weight:700; font-size:0.85rem; padding:3px 12px; '
        f'border-radius:20px; font-family:IBM Plex Mono,monospace; display:inline-block;">'
        f'{pct}%</span>'
    )


def mini_bar(val: float, color: str = BLUE) -> str:
    """Return an HTML mini progress bar for a 0-1 value."""
    pct = int(round(val * 100))
    return (
        f'<div style="height:5px; background:#eef1f5; border-radius:3px; overflow:hidden;">'
        f'<div style="width:{pct}%; height:100%; background:{color}; border-radius:3px;"></div>'
        f'</div>'
    )


def score_color(val: float) -> str:
    """Return a hex color representing the score quality."""
    if val >= 0.70:
        return GREEN
    if val >= 0.45:
        return ORANGE
    return RED


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Parse vector_score column into individual sub-score columns if present
    if "vector_score" in df.columns:
        def parse_vec(x):
            try:
                return ast.literal_eval(str(x))
            except Exception:
                return [np.nan] * 5

        vecs = df["vector_score"].apply(parse_vec)
        for i, key in enumerate(WEIGHT_KEYS):
            df[f"score_{key}"] = vecs.apply(
                lambda v, idx=i: v[idx] if isinstance(v, list) else np.nan
            )

    return df


df = load_data("results/pairs_scored.csv")

# ============================================================
# HEADER
# ============================================================

st.markdown(f"""
<div style="
    background: linear-gradient(135deg, {NAVY} 60%, #0D1E6B 100%);
    border-radius: 12px;
    padding: 24px 36px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 24px rgba(26,43,138,0.18);
    border-left: 5px solid {BLUE};
">
    <div>
        <p style="font-size:0.75rem; color:{BLUE}; text-transform:uppercase;
                  letter-spacing:0.18em; margin:0 0 4px 0; font-weight:600;">
            Talent Acquisition
        </p>
        <h1 style="font-size:1.6rem; font-weight:700; color:{WHITE};
                   letter-spacing:-0.02em; margin:0; line-height:1.2;">
            Espace Recrutement
        </h1>
    </div>
    <div style="text-align:right; line-height:1.05;">
        <div style="font-size:1.4rem; font-weight:800; color:{BLUE};
                    letter-spacing:-0.03em; font-family:'Sora',sans-serif;">
            forv/s
        </div>
        <div style="font-size:1.4rem; font-weight:800; color:{WHITE};
                    letter-spacing:-0.03em; font-family:'Sora',sans-serif;">
            mazars
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    # Custom logo replacing the default Streamlit icon
    st.markdown(f"""
    <div style="padding:20px 8px 8px 8px; text-align:center; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:8px;">
        <div style="font-size:1.25rem;font-weight:800;color:{BLUE};letter-spacing:-0.03em;font-family:'Sora',sans-serif;line-height:1.1;">forv/s</div>
        <div style="font-size:1.25rem;font-weight:800;color:{WHITE};letter-spacing:-0.03em;font-family:'Sora',sans-serif;line-height:1.1;">mazars</div>
        <div style="font-size:0.6rem;color:rgba(255,255,255,0.4);text-transform:uppercase;letter-spacing:0.2em;margin-top:6px;">Recrutement</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<span class="sidebar-label">Poste ciblé</span>', unsafe_allow_html=True)
    all_jobs     = sorted(df["job_id"].unique().tolist())
    selected_job = st.selectbox("Poste", all_jobs, label_visibility="collapsed")

    st.markdown('<span class="sidebar-label">Filtres</span>', unsafe_allow_html=True)
    min_score = st.slider("Score minimum", 0.0, 1.0, 0.30, 0.05)

    sectors       = ["Tous"] + sorted(df["sector"].dropna().unique().tolist())
    sector_filter = st.selectbox("Secteur candidat", sectors)

    st.markdown('<span class="sidebar-label">Priorités du recrutement</span>', unsafe_allow_html=True)
    st.markdown(
        '<span style="font-size:0.67rem; color:rgba(255,255,255,0.5); display:block; margin-bottom:10px;">'
        "Ajustez selon les exigences du poste. Les poids sont normalisés automatiquement."
        "</span>",
        unsafe_allow_html=True,
    )

    w_skills = st.slider("Compétences techniques", 0, 10, 7)
    w_exp    = st.slider("Expérience professionnelle", 0, 10, 5)
    w_edu    = st.slider("Formation / Diplômes", 0, 10, 3)
    w_lang   = st.slider("Langues", 0, 10, 2)
    w_sector = st.slider("Adéquation sectorielle", 0, 10, 3)

    raw = [w_skills, w_exp, w_edu, w_lang, w_sector]
    w_total  = sum(raw) or 1
    weights  = [w / w_total for w in raw]

    # Visual weight breakdown bar
    bar_colors = [BLUE, "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"]
    bar_html = '<div style="display:flex; height:8px; border-radius:4px; overflow:hidden; margin-top:10px;">'
    for w, c in zip(weights, bar_colors):
        bar_html += f'<div style="width:{w*100:.1f}%; background:{c};"></div>'
    bar_html += "</div>"
    st.markdown(bar_html, unsafe_allow_html=True)

    labels_short = ["Comp.", "Exp.", "Form.", "Lang.", "Sect."]
    rows = "".join(
        f'<div style="display:flex; justify-content:space-between; font-size:0.65rem; margin-top:5px;">'
        f'<span style="color:{bar_colors[i]}; font-weight:600;">{labels_short[i]}</span>'
        f'<span style="font-family:IBM Plex Mono,monospace; color:rgba(255,255,255,0.7);">{weights[i]*100:.0f}%</span>'
        f'</div>'
        for i in range(5)
    )
    st.markdown(
        f'<div style="background:rgba(255,255,255,0.06); border-radius:6px; padding:10px 12px; margin-top:8px;">{rows}</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# COMPUTE LIVE SCORES
# ============================================================

df_scored = df.copy()
df_scored["score_live"] = (
    df_scored["score_skills"]     * weights[0]
    + df_scored["score_experience"] * weights[1]
    + df_scored["score_education"]  * weights[2]
    + df_scored["score_languages"]  * weights[3]
    + df_scored["score_sector"]     * weights[4]
).clip(0.0, 1.0)

# Apply job and sector filters for the main shortlist view
job_df = df_scored[df_scored["job_id"] == selected_job].copy()

if sector_filter != "Tous":
    job_df = job_df[job_df["sector"] == sector_filter]

job_df = job_df[job_df["score_live"] >= min_score].sort_values("score_live", ascending=False).reset_index(drop=True)

# ============================================================
# KPI ROW
# ============================================================

k1, k2, k3, k4 = st.columns(4)

top_match    = job_df["score_live"].max() if len(job_df) > 0 else 0.0
strong_count = int((job_df["score_live"] >= 0.70).sum())
avg_score    = int(job_df["score_live"].mean() * 100) if len(job_df) > 0 else 0

k1.metric("Candidats analysés", f"{len(job_df)}")
k2.metric("Profils forts  (≥ 70%)", f"{strong_count}")
k3.metric("Meilleur score", f"{top_match*100:.2f}%")
k4.metric("Score moyen", f"{avg_score}%")

st.markdown("<hr>", unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "Shortlist du poste",
    "Fiche candidat",
    "Comparer deux candidats",
])

# ============================================================
# TAB 1 — SHORTLIST
# ============================================================

with tab1:
    st.markdown(
        f'<div class="section-title">Candidats classés — {selected_job}</div>',
        unsafe_allow_html=True,
    )

    if len(job_df) == 0:
        st.warning("Aucun candidat ne correspond aux critères. Abaissez le score minimum ou modifiez les filtres.")
    else:
        top_n = st.slider("Nombre de candidats affichés", 5, min(50, len(job_df)), min(15, len(job_df)), key="topn")

        for rank, (_, row) in enumerate(job_df.head(top_n).iterrows(), start=1):
            s         = row["score_live"]
            col_c     = score_color(s)
            pill_html = score_pill(s)

            # Build sub-score mini bars
            bars_html = '<div style="display:flex; gap:14px; margin-top:10px; flex-wrap:wrap;">'
            for label, key in zip(SCORE_LABELS, SCORE_KEYS):
                val = row.get(key, np.nan)
                if pd.isna(val):
                    continue
                pct = int(round(val * 100))
                bars_html += f"""
                <div style="min-width:70px; flex:1;">
                    <div style="font-size:0.6rem; color:{GRAY}; text-transform:uppercase;
                                letter-spacing:0.06em; margin-bottom:3px; font-weight:600;">
                        {label}
                    </div>
                    {mini_bar(val, col_c)}
                    <div style="font-size:0.62rem; color:{NAVY}; font-family:'IBM Plex Mono',monospace;
                                margin-top:2px; font-weight:600;">
                        {pct}%
                    </div>
                </div>"""
            bars_html += "</div>"

            sector_tag = (
                f'<span style="background:#EEF1F5; color:{GRAY}; font-size:0.65rem; '
                f'padding:2px 8px; border-radius:12px; font-weight:600;">'
                f'{row.get("sector", "—")}</span>'
            )

            st.markdown(f"""
            <div class="cand-card" style="border-left-color:{col_c};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div style="background:{NAVY}; color:{WHITE}; font-weight:700;
                                    font-size:0.85rem; width:30px; height:30px;
                                    border-radius:50%; display:flex; align-items:center;
                                    justify-content:center; flex-shrink:0;">
                            {rank}
                        </div>
                        <div>
                            <div style="font-weight:700; font-size:0.95rem; color:{NAVY};">
                                {row['candidate_id']}
                            </div>
                            <div style="margin-top:3px;">{sector_tag}</div>
                        </div>
                    </div>
                    <div>{pill_html}</div>
                </div>
                {bars_html}
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# TAB 2 — CANDIDATE PROFILE
# ============================================================

with tab2:
    st.markdown('<div class="section-title">Fiche candidat</div>', unsafe_allow_html=True)

    all_candidates = sorted(df_scored["candidate_id"].unique().tolist())
    selected_cand  = st.selectbox("Sélectionner un candidat", all_candidates, key="cand_profile")

    cand_df = df_scored[df_scored["candidate_id"] == selected_cand].sort_values("score_live", ascending=False)

    if len(cand_df) == 0:
        st.warning("Aucune donnée pour ce candidat.")
    else:
        best_row   = cand_df.iloc[0]
        best_score = best_row["score_live"]

        # Candidate header card
        st.markdown(f"""
        <div style="background:{NAVY}; border-radius:12px; padding:24px 28px;
                    display:flex; justify-content:space-between; align-items:center;
                    border-left:5px solid {BLUE}; margin-bottom:20px;">
            <div>
                <div style="font-size:0.7rem; color:{BLUE}; text-transform:uppercase;
                            letter-spacing:0.15em; font-weight:600; margin-bottom:4px;">Candidat</div>
                <div style="font-size:1.5rem; font-weight:700; color:{WHITE};">
                    {selected_cand}
                </div>
                <div style="margin-top:8px;">
                    <span style="background:rgba(255,255,255,0.12); color:{WHITE};
                                 font-size:0.72rem; padding:3px 12px; border-radius:12px;">
                        {best_row.get('sector', '—')}
                    </span>
                </div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.65rem; color:rgba(255,255,255,0.5);
                            text-transform:uppercase; letter-spacing:0.12em; margin-bottom:4px;">
                    Meilleur match
                </div>
                <div style="font-size:2.8rem; font-weight:700; color:{WHITE};
                            font-family:'IBM Plex Mono',monospace; line-height:1;">
                    {best_score*100:.2f}<span style="font-size:1.2rem; color:{BLUE};">%</span>
                </div>
                <div style="font-size:0.72rem; color:rgba(255,255,255,0.45); margin-top:4px;">
                    {best_row['job_id']}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_radar, col_jobs = st.columns([1, 1])

        with col_radar:
            st.markdown('<div class="section-title">Profil de compétences</div>', unsafe_allow_html=True)

            sub_scores  = [float(best_row.get(k, 0)) for k in SCORE_KEYS]
            sub_closed  = sub_scores + sub_scores[:1]
            cats_closed = SCORE_LABELS + [SCORE_LABELS[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=sub_closed,
                theta=cats_closed,
                fill="toself",
                fillcolor="rgba(0,153,216,0.15)",
                line=dict(color=BLUE, width=2.5),
                name="Profil",
            ))
            fig_radar.add_trace(go.Scatterpolar(
                r=sub_closed,
                theta=cats_closed,
                mode="markers",
                marker=dict(color=BLUE, size=7),
                showlegend=False,
            ))
            fig_radar.update_layout(
                polar=dict(
                    bgcolor=WHITE,
                    radialaxis=dict(
                        visible=True, range=[0, 1],
                        tickvals=[0.25, 0.5, 0.75, 1.0],
                        ticktext=["25", "50", "75", "100"],
                        tickfont=dict(size=8, color=GRAY, family="IBM Plex Mono"),
                        gridcolor="#dde5ef", linecolor="#dde5ef",
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=11, color=NAVY, family="Sora"),
                        gridcolor="#dde5ef", linecolor="#dde5ef",
                    ),
                ),
                showlegend=False,
                paper_bgcolor=WHITE,
                margin=dict(t=20, b=20, l=50, r=50),
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_jobs:
            st.markdown('<div class="section-title">Meilleurs postes pour ce candidat</div>', unsafe_allow_html=True)

            for _, jrow in cand_df.head(8).iterrows():
                s   = jrow["score_live"]
                pct = int(round(s * 100))
                c   = score_color(s)
                st.markdown(f"""
                <div style="background:{WHITE}; border-radius:8px; padding:12px 16px;
                            margin-bottom:8px; box-shadow:0 1px 6px rgba(26,43,138,0.07);
                            display:flex; align-items:center; justify-content:space-between;
                            border-left:3px solid {c};">
                    <div style="font-weight:600; font-size:0.88rem; color:{NAVY};">
                        {jrow['job_id']}
                    </div>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <div style="width:80px; height:5px; background:#eef1f5; border-radius:3px; overflow:hidden;">
                            <div style="width:{pct}%; height:100%; background:{c};"></div>
                        </div>
                        <span style="font-family:'IBM Plex Mono',monospace; font-weight:700;
                                     font-size:0.85rem; color:{c}; min-width:36px; text-align:right;">
                            {pct}%
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================
# TAB 3 — SIDE-BY-SIDE COMPARISON
# ============================================================

with tab3:
    st.markdown('<div class="section-title">Comparer deux candidats sur un même poste</div>', unsafe_allow_html=True)

    col_j, col_c1, col_c2 = st.columns(3)

    with col_j:
        cmp_job = st.selectbox("Poste", sorted(df_scored["job_id"].unique()), key="cmp_job")

    job_cands = sorted(df_scored[df_scored["job_id"] == cmp_job]["candidate_id"].unique())

    with col_c1:
        cand_a = st.selectbox("Candidat A", job_cands, key="cmp_a")

    with col_c2:
        default_b = 1 if len(job_cands) > 1 else 0
        cand_b    = st.selectbox("Candidat B", job_cands, index=default_b, key="cmp_b")

    row_a_df = df_scored[(df_scored["job_id"] == cmp_job) & (df_scored["candidate_id"] == cand_a)]
    row_b_df = df_scored[(df_scored["job_id"] == cmp_job) & (df_scored["candidate_id"] == cand_b)]

    if row_a_df.empty or row_b_df.empty:
        st.warning("Données manquantes pour l'un des candidats sur ce poste.")
    else:
        row_a   = row_a_df.iloc[0]
        row_b   = row_b_df.iloc[0]
        score_a = row_a["score_live"]
        score_b = row_b["score_live"]
        winner  = cand_a if score_a >= score_b else cand_b

        st.markdown("<hr>", unsafe_allow_html=True)

        # --- Global scores using native st.metric (no HTML) ---
        m_spacer1, m_a, m_mid, m_b, m_spacer2 = st.columns([1, 3, 1, 3, 1])

        with m_a:
            label_a = f"Candidat A — {cand_a}" + (" ✓ Recommandé" if winner == cand_a else "")
            st.metric(label_a, f"{score_a*100:.2f}%")

        with m_mid:
            st.markdown(
                f"<div style='text-align:center; padding-top:28px; font-size:1.2rem;"
                f" color:{GRAY}; font-weight:300;'>vs</div>",
                unsafe_allow_html=True,
            )

        with m_b:
            label_b = f"Candidat B — {cand_b}" + (" ✓ Recommandé" if winner == cand_b else "")
            st.metric(label_b, f"{score_b*100:.2f}%")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Détail par critère</div>', unsafe_allow_html=True)

        # --- Mirror bar chart using Plotly (fully reliable) ---
        # Values for A go negative (left side), values for B go positive (right side)
        vals_a   = [-float(row_a.get(k, 0)) * 100 for k in SCORE_KEYS]
        vals_b   = [ float(row_b.get(k, 0)) * 100  for k in SCORE_KEYS]
        labels_r = SCORE_LABELS[::-1]   # reverse so Skills is on top
        vals_a_r = vals_a[::-1]
        vals_b_r = vals_b[::-1]

        fig_cmp = go.Figure()

        # Candidate A bars (negative = left)
        fig_cmp.add_trace(go.Bar(
            name=cand_a,
            y=labels_r,
            x=vals_a_r,
            orientation="h",
            marker_color=NAVY,
            text=[f"{abs(v):.0f}%" for v in vals_a_r],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11, color=NAVY),
            hovertemplate="%{text}<extra>" + cand_a + "</extra>",
        ))

        # Candidate B bars (positive = right)
        fig_cmp.add_trace(go.Bar(
            name=cand_b,
            y=labels_r,
            x=vals_b_r,
            orientation="h",
            marker_color=BLUE,
            text=[f"{v:.0f}%" for v in vals_b_r],
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=11, color=NAVY),
            hovertemplate="%{text}<extra>" + cand_b + "</extra>",
        ))

        fig_cmp.update_layout(
            barmode="overlay",
            paper_bgcolor=WHITE,
            plot_bgcolor=WHITE,
            font_family="Sora, sans-serif",
            margin=dict(t=20, b=20, l=120, r=80),
            height=280,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11, family="Sora"),
            ),
            xaxis=dict(
                range=[-110, 110],
                tickvals=[-100, -75, -50, -25, 0, 25, 50, 75, 100],
                ticktext=["100%", "75%", "50%", "25%", "0", "25%", "50%", "75%", "100%"],
                showgrid=True,
                gridcolor="#eef1f5",
                zeroline=True,
                zerolinecolor=NAVY,
                zerolinewidth=2,
                tickfont=dict(size=9, color=GRAY, family="IBM Plex Mono"),
            ),
            yaxis=dict(
                tickfont=dict(size=11, color=NAVY, family="Sora"),
                showgrid=False,
            ),
        )

        # Color winning bars
        for i, (va, vb) in enumerate(zip(vals_a_r, vals_b_r)):
            if abs(va) >= abs(vb):
                fig_cmp.data[0].marker.color = [
                    NAVY if abs(vals_a_r[j]) >= abs(vals_b_r[j]) else "#C7D0E8"
                    for j in range(len(vals_a_r))
                ]
            else:
                fig_cmp.data[1].marker.color = [
                    BLUE if abs(vals_b_r[j]) > abs(vals_a_r[j]) else "#A8D8EE"
                    for j in range(len(vals_b_r))
                ]

        st.plotly_chart(fig_cmp, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================

st.markdown(f"""
<div style="margin-top:40px; padding:16px 24px; background:{NAVY}; border-radius:10px;
            display:flex; justify-content:space-between; align-items:center;">
    <span style="color:rgba(255,255,255,0.4); font-size:0.68rem; letter-spacing:0.08em;">
        FORVIS MAZARS &mdash; TALENT ACQUISITION INTELLIGENCE
    </span>
    <span style="color:{BLUE}; font-size:0.68rem; font-family:'IBM Plex Mono',monospace;">
        ATS Dashboard v3
    </span>
</div>
""", unsafe_allow_html=True)