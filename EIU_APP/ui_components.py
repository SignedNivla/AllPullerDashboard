import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Palette
#   #30364F  bg · #262B3E deep · #3D4460 mid · #1E2333 deeper
#   #ACBAC4  muted · #E1D9BC sand · #F0F0DB cream · #5A6080 dim
#   #7DBFA0  success
# ─────────────────────────────────────────────────────────────────────────────

def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');

    /* ══════════════════════════════════════════════════════════════════════════
       BUTTONS
    ══════════════════════════════════════════════════════════════════════════ */
    button[kind="primary"] {
        background: #E1D9BC !important; color: #30364F !important;
        border: none !important; font-weight: 700 !important;
        transition: background 0.15s !important;
    }
    button[kind="primary"]:hover    { background: #F0F0DB !important; }
    button[kind="primary"]:disabled { background: #3D4460 !important; color: #5A6080 !important; }

    button[kind="secondary"] {
        background: transparent !important; border: 1px solid #3D4460 !important;
        color: #ACBAC4 !important; transition: border-color 0.15s, color 0.15s !important;
    }
    button[kind="secondary"]:hover {
        border-color: #E1D9BC !important; color: #F0F0DB !important;
        background: transparent !important;
    }
    button[kind="downloadButton"] {
        background: transparent !important; border: 1px solid #3D4460 !important; color: #ACBAC4 !important;
    }
    button[kind="downloadButton"]:hover { border-color: #E1D9BC !important; color: #F0F0DB !important; }

    /* ══════════════════════════════════════════════════════════════════════════
       DEEP OVERRIDES
    ══════════════════════════════════════════════════════════════════════════ */
    div[data-testid="stExpander"] {
        border: 1px solid #3D4460 !important; border-radius: 8px !important; background: #1E2333 !important;
    }
    div[data-testid="stExpander"] summary { background: #1E2333 !important; color: #ACBAC4 !important; }
    div[data-testid="stExpander"] summary:hover { color: #F0F0DB !important; background: #262B3E !important; }
    div[data-testid="stExpander"] > div { background: #1E2333 !important; }

    div[data-testid="stCheckbox"] label       { color: #ACBAC4 !important; font-size: 13px !important; }
    div[data-testid="stCheckbox"] label:hover { color: #F0F0DB !important; }

    div[data-testid="stTextInput"] input {
        background: #1E2333 !important; border: 1px solid #3D4460 !important;
        color: #F0F0DB !important; border-radius: 7px !important; font-size: 13px !important;
    }
    div[data-testid="stTextInput"] input:focus       { border-color: #ACBAC4 !important; box-shadow: none !important; }
    div[data-testid="stTextInput"] input::placeholder { color: #5A6080 !important; }

    div[data-testid="stNumberInput"] input  { background: #1E2333 !important; border: 1px solid #3D4460 !important; color: #F0F0DB !important; }
    div[data-testid="stNumberInput"] button { background: #262B3E !important; border-color: #3D4460 !important; color: #ACBAC4 !important; }
    div[data-testid="stNumberInput"] button:hover { background: #3D4460 !important; color: #F0F0DB !important; }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #1E2333 !important; border: 1px solid #3D4460 !important; color: #F0F0DB !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover { border-color: #ACBAC4 !important; }

    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background: #1E2333 !important; border: 1px solid #3D4460 !important; color: #F0F0DB !important;
    }
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] { background: #3D4460 !important; color: #F0F0DB !important; }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #1E2333 !important; border-color: #3D4460 !important;
        border-radius: 10px !important; transition: border-color 0.2s !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #ACBAC4 !important; }

    div[data-testid="stDataFrame"]    { border: 1px solid #3D4460 !important; border-radius: 8px !important; }
    hr                                { border-color: #3D4460 !important; }
    div[data-testid="stAlert"]        { background: #262B3E !important; border: 1px solid #3D4460 !important; color: #ACBAC4 !important; border-radius: 8px !important; }
    div[data-testid="stStatusWidget"] { background: #262B3E !important; border: 1px solid #3D4460 !important; }

    div[data-testid="stTabs"] button[role="tab"]                       { color: #ACBAC4 !important; font-size: 15px !important; font-weight: 600 !important; padding: 8px 20px !important; }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { color: #F0F0DB !important; }
    div[data-testid="stTabs"] button[role="tab"]:hover                 { color: #E1D9BC !important; }

    /* ══════════════════════════════════════════════════════════════════════════
       ZONE A — PANEL CARDS
    ══════════════════════════════════════════════════════════════════════════ */
    .panel-header {
        display: flex; align-items: center; gap: 8px;
        padding: 12px 14px 10px;
        border-bottom: 1px solid #3D4460;
        background: #1E2333;
        border-radius: 10px 10px 0 0;
    }
    .panel-label {
        font-size: 10px; font-weight: 700; color: #ACBAC4;
        letter-spacing: 2px; text-transform: uppercase; flex: 1;
    }
    .count-badge {
        font-size: 10px; font-weight: 700; padding: 2px 10px;
        border-radius: 20px; transition: all 0.2s;
    }
    .count-badge.active {
        background: rgba(225,217,188,0.15);
        border: 1px solid rgba(225,217,188,0.4);
        color: #E1D9BC;
    }
    .count-badge.empty {
        background: transparent; border: 1px solid #3D4460; color: #5A6080;
    }
    .selection-bar-wrap {
        height: 2px; background: #3D4460; border-radius: 1px;
        margin: 0 0 6px 0; overflow: hidden;
    }
    .selection-bar-fill {
        height: 100%; border-radius: 1px; background: #E1D9BC; transition: width 0.3s ease;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ZONE A — RIGHT PANEL
    ══════════════════════════════════════════════════════════════════════════ */
    .right-card {
        background: #262B3E; border: 1px solid #3D4460;
        border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
    }
    .right-card-label {
        font-size: 10px; font-weight: 700; color: #ACBAC4;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px;
    }
    .ring-row { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
    .ring-row-label { font-size: 11px; color: #5A6080; width: 68px; flex-shrink: 0; }
    .ring-row-bar   { flex: 1; height: 3px; background: #3D4460; border-radius: 2px; overflow: hidden; }
    .ring-row-fill  { height: 100%; border-radius: 2px; background: #E1D9BC; transition: width 0.3s ease; }
    .ring-row-val   { font-size: 11px; font-weight: 700; color: #E1D9BC; min-width: 36px; text-align: right; }
    .ring-row-val.empty { color: #5A6080; font-weight: 400; }
    .year-row {
        display: flex; align-items: center; justify-content: space-between;
        padding-top: 10px; margin-top: 6px; border-top: 1px solid #3D4460; font-size: 11px;
    }
    .year-row-label { color: #5A6080; }
    .year-row-val   { color: #F0F0DB; font-weight: 600; }
    .year-row-sub   { color: #5A6080; font-weight: 400; }
    .hint-row       { font-size: 10px; color: #5A6080; line-height: 1.8; margin-top: 6px; }

    /* ══════════════════════════════════════════════════════════════════════════
       ZONE C — RESULT STRIP
    ══════════════════════════════════════════════════════════════════════════ */
    .result-strip-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 10px 16px;
        background: rgba(125,191,160,0.10);
        border: 1px solid rgba(125,191,160,0.28);
        border-radius: 10px 10px 0 0;
        margin-top: 16px;
    }
    .result-strip-dot  { color: #7DBFA0; font-size: 9px; }
    .result-strip-rows { font-size: 13px; font-weight: 700; color: #F0F0DB; }
    .result-strip-meta { font-size: 11px; color: #ACBAC4; }
    .result-strip-sep  { color: #3D4460; margin: 0 5px; }

    .actions-bar {
        background: #262B3E;
        border: 1px solid #3D4460; border-top: none;
        padding: 6px 8px;
    }
    .actions-bar.rounded-bottom { border-radius: 0 0 10px 10px; }

    .vdivider {
        display: inline-block; width: 1px; height: 26px;
        background: #3D4460; vertical-align: middle; margin: 0 4px;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ZONE D — BULK DOWNLOAD
    ══════════════════════════════════════════════════════════════════════════ */
    .dl-outer {
        border: 1px solid #3D4460; border-radius: 12px;
        overflow: hidden; margin-top: 16px;
    }
    .dl-header {
        display: flex; align-items: center; justify-content: space-between;
        padding: 11px 18px;
        border-bottom: 1px solid #3D4460;
        background: #1E2333;
    }
    .dl-header-left { display: flex; align-items: center; gap: 0; }
    .dl-card-title  { font-size: 10px; font-weight: 700; color: #ACBAC4; letter-spacing: 2px; text-transform: uppercase; }
    .dl-card-sub    { font-size: 10px; color: #5A6080; margin-left: 10px; }
    .dl-body        { padding: 16px 18px; display: flex; align-items: flex-start; gap: 20px; background: #262B3E; }

    .dl-steps       { display: flex; flex-direction: column; gap: 10px; min-width: 190px; }
    .dl-step        { display: flex; align-items: center; gap: 9px; transition: opacity 0.3s; }
    .dl-step.dim    { opacity: 0.3; }
    .dl-step-circle {
        width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: 700; transition: all 0.3s;
    }
    .dl-step-circle.done   { background: #E1D9BC; color: #30364F; }
    .dl-step-circle.active { background: transparent; border: 1.5px solid #E1D9BC; color: #E1D9BC; }
    .dl-step-circle.idle   { background: transparent; border: 1.5px solid #3D4460; color: #5A6080; }
    .dl-step-text          { font-size: 11px; }
    .dl-step-text.done     { color: #E1D9BC; }
    .dl-step-text.active   { color: #F0F0DB; }
    .dl-step-text.idle     { color: #ACBAC4; }

    .dl-status-area  { flex: 1; }
    .dl-status-desc  { font-size: 12px; color: #F0F0DB; margin-bottom: 4px; font-weight: 500; }
    .dl-status-sub   { font-size: 10px; color: #5A6080; line-height: 1.7; }
    .dl-id-chip {
        font-size: 11px; font-family: 'DM Mono', monospace; color: #E1D9BC;
        background: rgba(61,68,96,0.5); border: 1px solid #3D4460;
        border-radius: 6px; padding: 6px 10px; word-break: break-all;
        margin: 4px 0 6px; display: block;
    }
    .dl-shimmer-wrap { height: 3px; background: #3D4460; border-radius: 2px; overflow: hidden; margin-top: 10px; }
    .dl-shimmer-fill {
        height: 100%; border-radius: 2px;
        background: linear-gradient(90deg, #3D4460 25%, #E1D9BC 50%, #3D4460 75%);
        background-size: 400px 100%;
        animation: dlshimmer 1.2s linear infinite;
        width: 100%;
    }
    @keyframes dlshimmer { 0% { background-position:-400px 0; } 100% { background-position:400px 0; } }

    .dl-ready-link {
        display: inline-block; margin-top: 8px; padding: 8px 18px;
        background: #7DBFA0; color: #1a2e25; border-radius: 7px;
        font-size: 11px; font-weight: 700; text-decoration: none;
        letter-spacing: 0.5px; transition: opacity 0.15s;
    }
    .dl-ready-link:hover { opacity: 0.88; color: #1a2e25; }

    /* ══════════════════════════════════════════════════════════════════════════
       ARTICLE & REPORT CARDS
    ══════════════════════════════════════════════════════════════════════════ */
    .art-card-badge {
        display: inline-block; background: #E1D9BC; color: #30364F;
        font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
        text-transform: uppercase; padding: 2px 9px; border-radius: 20px;
        margin-bottom: 8px; width: fit-content;
    }
    .art-card-title {
        font-size: 15px; font-weight: 700; color: #F0F0DB; line-height: 1.45;
        height: calc(1.45em * 3); display: -webkit-box; -webkit-line-clamp: 3;
        -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 6px;
    }
    .rep-card-desc {
        font-size: 12px; color: #ACBAC4; line-height: 1.55;
        height: calc(1.55em * 2); display: -webkit-box; -webkit-line-clamp: 2;
        -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 10px;
    }
    .art-card-meta {
        display: flex; align-items: center; gap: 12px; font-size: 11px; color: #ACBAC4;
        border-top: 1px solid #3D4460; padding-top: 8px; margin-top: 4px; margin-bottom: 8px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"] {
        background: transparent !important; border: 1px solid #3D4460 !important;
        color: #ACBAC4 !important; font-size: 12px !important; border-radius: 8px !important;
        transition: border-color 0.2s, color 0.2s !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"]:hover {
        border-color: #E1D9BC !important; color: #F0F0DB !important; background: transparent !important;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       SHARED
    ══════════════════════════════════════════════════════════════════════════ */
    .section-label {
        font-size: 10px !important; font-weight: 700 !important; color: #ACBAC4 !important;
        letter-spacing: 2px !important; text-transform: uppercase !important;
        margin-bottom: 6px !important; line-height: 1.4 !important;
    }
    .result-pill {
        display: inline-block; background: #262B3E; color: #ACBAC4;
        font-size: 13px; font-weight: 600; padding: 5px 16px;
        border-radius: 20px; border: 1px solid #3D4460; margin-bottom: 10px;
    }
    .active-report-strip {
        background: #262B3E; border: 1px solid #3D4460; border-radius: 12px;
        padding: 14px 20px; margin-bottom: 20px; display: flex; flex-direction: column; gap: 4px;
    }
    .active-report-strip-name { font-size: 15px; font-weight: 700; color: #F0F0DB; }
    .active-report-strip-meta { font-size: 11px; color: #ACBAC4; }
    .result-meta-row { font-size: 11px; color: #ACBAC4; padding: 4px 0 8px; }
    .result-meta-row span { color: #F0F0DB; font-weight: 700; }
    .page-info { text-align: center; padding-top: 8px; color: #ACBAC4; font-size: 13px; }
    .page-info b { color: #F0F0DB; }
    .summary-box {
        background: #1E2333; border: 1px solid #3D4460; border-radius: 8px;
        padding: 10px 12px; font-size: 11px; color: #ACBAC4; line-height: 1.8; margin: 8px 0;
    }
    .summary-box b { color: #ACBAC4; font-size: 10px; letter-spacing: 1px; text-transform: uppercase; }
    .summary-box .val { color: #F0F0DB; font-weight: 700; }
    .summary-box .dim { color: #5A6080; }
    .hint-text { font-size: 11px; color: #5A6080; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
def render_header(db_connected, db_name=""):
    h1, h2, h3 = st.columns([1, 3, 1.2])
    with h1:
        st.markdown("<span style='font-size:22px; font-weight:800; color:#F0F0DB;'>EIU</span>",
                    unsafe_allow_html=True)
    with h2:
        st.markdown("<h3 style='text-align:center; letter-spacing:3px; color:#ACBAC4; "
                    "font-weight:400; opacity:0.8;'>DATA PULL PLATFORM</h3>",
                    unsafe_allow_html=True)
    with h3:
        if db_connected:
            st.markdown(f"<div style='text-align:right'><span style='font-size:12px; color:#E1D9BC;'>🟢 {db_name}</span></div>",
                        unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:right'><span style='font-size:12px; color:#5A6080;'>⚪ Offline</span></div>",
                        unsafe_allow_html=True)
    st.divider()


# ─────────────────────────────────────────────────────────────────────────────
# ZONE A — PANEL HEADER  (rendered above tree container)
# ─────────────────────────────────────────────────────────────────────────────
def render_panel_header(title, selected, total):
    """
    Panel top bar with label, count badge, and thin selection bar.
    `selected` comes from session_state cache (prev render cycle) so it's
    always one cycle behind on first check — acceptable for a display counter.
    """
    badge_cls = "active" if selected > 0 else "empty"
    badge_txt = f"{selected}&thinsp;/&thinsp;{total}" if total > 0 else "—"
    bar_pct   = int(selected / total * 100) if total > 0 else 0
    st.markdown(f"""
    <div class="panel-header">
        <span class="panel-label">{title}</span>
        <span class="count-badge {badge_cls}">{badge_txt}</span>
    </div>
    <div class="selection-bar-wrap">
        <div class="selection-bar-fill" style="width:{bar_pct}%"></div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ZONE A — RIGHT PANEL  (ringkasan card with progress bars)
# ─────────────────────────────────────────────────────────────────────────────
def render_right_panel(n_ind, n_ind_total, n_geo, n_geo_total, year_from, year_to):
    pct_ind  = int(n_ind / n_ind_total * 100) if n_ind_total > 0 else 0
    pct_geo  = int(n_geo / n_geo_total * 100) if n_geo_total > 0 else 0
    ind_cls  = "" if n_ind > 0 else "empty"
    geo_cls  = "" if n_geo > 0 else "empty"
    ind_val  = f"{n_ind}<span style='color:#5A6080;font-weight:400'>/{n_ind_total}</span>" if n_ind_total else "—"
    geo_val  = f"{n_geo}<span style='color:#5A6080;font-weight:400'>/{n_geo_total}</span>" if n_geo_total else "—"
    yr_span  = year_to - year_from + 1

    hints = ""
    if n_ind == 0: hints += "<div>· Pilih indikator</div>"
    if n_geo == 0: hints += "<div>· Pilih negara</div>"
    if hints:
        hints = f'<div class="hint-row">{hints}</div>'

    st.markdown(f"""
    <div class="right-card">
        <div class="right-card-label">Ringkasan</div>
        <div class="ring-row">
            <span class="ring-row-label">Indikator</span>
            <div class="ring-row-bar"><div class="ring-row-fill" style="width:{pct_ind}%"></div></div>
            <span class="ring-row-val {ind_cls}">{ind_val}</span>
        </div>
        <div class="ring-row">
            <span class="ring-row-label">Negara</span>
            <div class="ring-row-bar"><div class="ring-row-fill" style="width:{pct_geo}%"></div></div>
            <span class="ring-row-val {geo_cls}">{geo_val}</span>
        </div>
        <div class="year-row">
            <span class="year-row-label">Tahun</span>
            <span>
                <span class="year-row-val">{year_from} – {year_to}</span>
                <span class="year-row-sub"> ({yr_span}y)</span>
            </span>
        </div>
        {hints}
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ZONE C — RESULT STRIP HEADER
# ─────────────────────────────────────────────────────────────────────────────
def render_result_strip_header(df):
    rows = f"{len(df):,}"
    cols = len(df.columns)
    st.markdown(f"""
    <div class="result-strip-header">
        <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
            <span class="result-strip-dot">●</span>
            <span class="result-strip-rows">{rows} baris</span>
            <span class="result-strip-sep">·</span>
            <span class="result-strip-meta">{cols} kolom</span>
        </div>
        <span style="font-size:10px; color:#5A6080; letter-spacing:1px;">HASIL PULL</span>
    </div>
    """, unsafe_allow_html=True)


def render_actions_bar_open(rounded_bottom=True):
    """Opens the actions bar div (must be closed with render_actions_bar_close)."""
    cls = "actions-bar rounded-bottom" if rounded_bottom else "actions-bar"
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)


def render_actions_bar_close():
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ZONE D — BULK DOWNLOAD CARD
# ─────────────────────────────────────────────────────────────────────────────
def render_dl_card_outer_open():
    st.markdown('<div class="dl-outer">', unsafe_allow_html=True)


def render_dl_card_outer_close():
    st.markdown('</div>', unsafe_allow_html=True)


def render_dl_header(dl_format, dl_format_key):
    """Header bar: title + sub + format toggle buttons."""
    st.markdown("""
    <div class="dl-header">
        <div class="dl-header-left">
            <span class="dl-card-title">Bulk Export</span>
            <span class="dl-card-sub">&nbsp;·&nbsp; Server-side &nbsp;·&nbsp; ~5 menit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_dl_steps(phase):
    """3-step tracker HTML."""
    steps = [
        ("1", "Request export",  phase != "idle"),
        ("2", "Poll for file",   phase in ("polling", "ready")),
        ("3", "Download file",   phase == "ready"),
    ]
    active_map = {"idle": 0, "requested": 1, "polling": 2, "ready": -1}
    active_idx = active_map.get(phase, 0)

    html = '<div class="dl-steps">'
    for i, (n, lbl, done) in enumerate(steps):
        is_active  = (i == active_idx) and not done
        dim        = not (done or is_active)
        circle_cls = "done" if done else ("active" if is_active else "idle")
        text_cls   = "done" if done else ("active" if is_active else "idle")
        dim_cls    = "dim" if dim else ""
        symbol     = "✓" if done else n
        html += (f'<div class="dl-step {dim_cls}">'
                 f'<div class="dl-step-circle {circle_cls}">{symbol}</div>'
                 f'<span class="dl-step-text {text_cls}">{lbl}</span>'
                 f'</div>')
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_dl_status(phase, dl_id, dl_status, dl_link, dl_format, can_request):
    """Status text area content changes per phase."""
    if phase == "idle":
        msg = (f"Export seleksi sebagai <b>{dl_format}</b>"
               if can_request else
               "Pilih indikator &amp; negara terlebih dahulu.")
        st.markdown(f'<div class="dl-status-desc">{msg}</div>'
                    '<div class="dl-status-sub">File diproses server EIU · biasanya siap ~5 menit.</div>',
                    unsafe_allow_html=True)

    elif phase == "requested":
        st.markdown(f'<div class="dl-status-sub">Download ID</div>'
                    f'<code class="dl-id-chip">{dl_id}</code>'
                    '<div class="dl-status-sub">Request diterima. Klik Poll Status untuk mengecek.</div>',
                    unsafe_allow_html=True)

    elif phase == "polling":
        poll = dl_status or {}
        code = poll.get("statusCode", "")
        msg  = poll.get("message", "")
        err  = poll.get("errorMessage", "")
        sub  = f"Status: {code}" if code else "Memproses..."
        if msg: sub += f" · {msg}"
        st.markdown(f'<div class="dl-status-desc">EIU memproses file...</div>'
                    f'<div class="dl-status-sub">{sub}</div>'
                    '<div class="dl-shimmer-wrap"><div class="dl-shimmer-fill"></div></div>',
                    unsafe_allow_html=True)
        if err:
            st.error(f"Error: {err}")

    elif phase == "ready":
        st.markdown(f'<div class="dl-status-desc" style="color:#7DBFA0;">File siap diunduh</div>'
                    f'<div class="dl-status-sub">Format: {dl_format} · Link aktif 24 jam.</div>'
                    f'<a class="dl-ready-link" href="{dl_link}" target="_blank">↓ Download {dl_format}</a>',
                    unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SHARED HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def render_section_label(text):
    st.markdown(f'<p class="section-label">{text}</p>', unsafe_allow_html=True)


def render_result_meta(df):
    st.markdown(
        f'<div class="result-meta-row">'
        f'<span>{len(df):,}</span> baris &nbsp;·&nbsp; '
        f'<span>{len(df.columns)}</span> kolom</div>',
        unsafe_allow_html=True
    )


def render_page_info(current, total):
    st.markdown(
        f'<p class="page-info">Halaman <b>{current}</b> dari <b>{total}</b></p>',
        unsafe_allow_html=True
    )


def render_summary_box(n_ind, n_geo, year_from, year_to):
    """Legacy — kept for non-data-pull tabs."""
    ind_val = f'<span class="val">{n_ind}</span>' if n_ind > 0 else '<span class="dim">0</span>'
    geo_val = f'<span class="val">{n_geo}</span>' if n_geo > 0 else '<span class="dim">0</span>'
    st.markdown(
        f'<div class="summary-box"><b>Ringkasan</b><br>'
        f'{ind_val} indikator<br>{geo_val} negara<br>'
        f'<span class="dim">{year_from}–{year_to}</span></div>',
        unsafe_allow_html=True
    )


def render_hints(n_ind, n_geo):
    hints = []
    if n_ind == 0: hints.append("· Pilih indikator")
    if n_geo == 0: hints.append("· Pilih negara")
    if hints:
        st.markdown('<div class="hint-text">' + "<br>".join(hints) + '</div>',
                    unsafe_allow_html=True)


def count_leaves(nodes):
    """Count leaf nodes in a reference tree for denominator display."""
    total = 0
    for n in nodes:
        if n.get("children"):
            total += count_leaves(n["children"])
        else:
            total += 1
    return total


def flatten_tree(nodes, prefix=""):
    """
    Flatten a reference tree into (display_label, node_id) tuples for multiselect.
    Only leaf nodes included. Label: Parent > Child > Leaf
    """
    result = []
    for node in nodes:
        name     = node.get("name", "?")
        node_id  = node.get("id")
        children = node.get("children") or []
        path     = f"{prefix} > {name}" if prefix else name
        if children:
            result.extend(flatten_tree(children, path))
        else:
            result.append((path, node_id))
    return result


def render_grouped_multiselect(nodes, key_prefix, selected_ids_list, label="Item", query=""):
    """
    Render one st.expander per top-level group, each with a st.multiselect.
    Appends selected node_ids into selected_ids_list.
    If query is set, shows a flat universal search result instead of grouped view.
    """
    q = query.strip().lower()

    if q:
        # ── Universal search mode: flat list across all groups ────────────────
        all_leaves = flatten_tree(nodes, prefix="")
        matched    = [(lbl, nid) for lbl, nid in all_leaves if q in lbl.lower()]

        if not matched:
            st.markdown(
                f"<div style='color:#5A6080; font-size:12px; padding:8px;'>"
                f"Tidak ada hasil untuk <b>{query}</b></div>",
                unsafe_allow_html=True
            )
            return

        leaf_labels = [lbl for lbl, _ in matched]
        leaf_map    = {lbl: nid for lbl, nid in matched}
        key         = f"{key_prefix}_search_results"

        # Keep existing selections across modes
        existing = st.session_state.get(key, [])
        valid_existing = [l for l in existing if l in leaf_labels]

        chosen = st.multiselect(
            label,
            options=leaf_labels,
            default=valid_existing,
            key=key,
            label_visibility="collapsed",
            placeholder=f"{len(matched)} hasil ditemukan...",
        )
        for lbl in chosen:
            if leaf_map[lbl] not in selected_ids_list:
                selected_ids_list.append(leaf_map[lbl])

    else:
        # ── Normal grouped mode ───────────────────────────────────────────────
        for gi, group in enumerate(nodes):
            group_name = group.get("name", "?")
            children   = group.get("children") or []

            if children:
                leaves = flatten_tree(children, prefix="")
            else:
                leaves = [(group_name, group.get("id"))]

            if not leaves:
                continue

            leaf_labels = [lbl for lbl, _ in leaves]
            leaf_map    = {lbl: nid for lbl, nid in leaves}
            key         = f"{key_prefix}_grp_{gi}"

            with st.expander(f"{group_name}  ({len(leaves)})", expanded=False):
                chosen = st.multiselect(
                    label,
                    options=leaf_labels,
                    key=key,
                    label_visibility="collapsed",
                    placeholder=f"Pilih dari {group_name}...",
                )
                for lbl in chosen:
                    selected_ids_list.append(leaf_map[lbl])


def select_all_groups(nodes, key_prefix, select=True):
    """
    Set all grouped multiselect keys to all options (select=True) or [] (select=False).
    Call this from on_change of a Select All / Clear All button.
    """
    for gi, group in enumerate(nodes):
        children = group.get("children") or []
        if children:
            leaves = flatten_tree(children, prefix="")
        else:
            leaves = [(group.get("name", "?"), group.get("id"))]
        leaf_labels = [lbl for lbl, _ in leaves]
        key = f"{key_prefix}_grp_{gi}"
        st.session_state[key] = leaf_labels if select else []


# ─────────────────────────────────────────────────────────────────────────────
# TREE
# ─────────────────────────────────────────────────────────────────────────────
def toggle_all_global(prefix, nodes, master_key):
    """
    Set all leaf checkboxes. Key = {prefix}_leaf_{numeric_path}
    where numeric_path is the positional index chain (e.g. '0_2_1').
    Must match the key scheme in render_tree exactly.
    """
    status = st.session_state[master_key]

    def walk(data, ipath=""):
        for i, node in enumerate(data):
            cur = f"{ipath}_{i}" if ipath else str(i)
            children = node.get("children") or []
            if children:
                walk(children, cur)
            else:
                st.session_state[f"{prefix}_leaf_{cur}"] = status

    walk(nodes)


def render_tree(node, level, key_prefix, selected_list, query="", idx=0, ipath="", parent=""):
    """
    Render tree node recursively.
    ipath = numeric index chain built from root (e.g. '0_2_1') — always unique.
    Leaf key = {key_prefix}_leaf_{ipath} — must match toggle_all_global.
    """
    name     = node.get("name", "Unknown")
    node_id  = node.get("id")
    children = node.get("children") or []

    cur_ipath = f"{ipath}_{idx}" if ipath else str(idx)

    # Skip redundant wrapper (name == parent)
    if name == parent and children:
        for i, c in enumerate(children):
            render_tree(c, level, key_prefix, selected_list, query, i, cur_ipath, name)
        return

    # Filter by search query
    if query and query.lower() not in name.lower():
        if not children or not any(query.lower() in c.get("name", "").lower() for c in children):
            return

    if children:
        with st.expander(name, expanded=bool(query)):
            for i, c in enumerate(children):
                render_tree(c, level + 1, key_prefix, selected_list, query, i, cur_ipath, name)
    else:
        if st.checkbox(name, key=f"{key_prefix}_leaf_{cur_ipath}"):
            selected_list.append(node_id)