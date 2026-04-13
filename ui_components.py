import streamlit as st
def apply_styles():
    st.markdown("""
    <style>
    /* ══════════════════════════════════════════════════════════════════════════
       BUTTONS
    ══════════════════════════════════════════════════════════════════════════ */

    /* Primary — warm sand bg, dark navy text */
    button[kind="primary"] {
        background: #E1D9BC !important;
        color: #30364F !important;
        border: none !important;
        font-weight: 700 !important;
        transition: background 0.15s !important;
    }
    button[kind="primary"]:hover {
        background: #F0F0DB !important;
        color: #30364F !important;
    }
    button[kind="primary"]:disabled {
        background: #3D4460 !important;
        color: #5A6080 !important;
    }

    /* Secondary — bordered, muted */
    button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #3D4460 !important;
        color: #ACBAC4 !important;
        transition: border-color 0.15s, color 0.15s !important;
    }
    button[kind="secondary"]:hover {
        border-color: #E1D9BC !important;
        color: #F0F0DB !important;
        background: transparent !important;
    }

    /* Download */
    button[kind="downloadButton"] {
        background: transparent !important;
        border: 1px solid #3D4460 !important;
        color: #ACBAC4 !important;
    }
    button[kind="downloadButton"]:hover {
        border-color: #E1D9BC !important;
        color: #F0F0DB !important;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       DEEP COMPONENT OVERRIDES
    ══════════════════════════════════════════════════════════════════════════ */

    /* Expander */
    div[data-testid="stExpander"] {
        border: 1px solid #3D4460 !important;
        border-radius: 8px !important;
        background: #262B3E !important;
    }
    div[data-testid="stExpander"] summary {
        background: #262B3E !important;
        color: #ACBAC4 !important;
    }
    div[data-testid="stExpander"] summary:hover {
        color: #F0F0DB !important;
        background: #2E3450 !important;
    }
    div[data-testid="stExpander"] > div {
        background: #262B3E !important;
    }

    /* Checkbox */
    div[data-testid="stCheckbox"] label { color: #ACBAC4 !important; }
    div[data-testid="stCheckbox"] label:hover { color: #F0F0DB !important; }

    /* Text inputs */
    div[data-testid="stTextInput"] input {
        background: #262B3E !important;
        border: 1px solid #3D4460 !important;
        color: #F0F0DB !important;
        border-radius: 7px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #ACBAC4 !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #5A6080 !important; }

    /* Number inputs */
    div[data-testid="stNumberInput"] input {
        background: #262B3E !important;
        border: 1px solid #3D4460 !important;
        color: #F0F0DB !important;
    }
    div[data-testid="stNumberInput"] button {
        background: #2E3450 !important;
        border-color: #3D4460 !important;
        color: #ACBAC4 !important;
    }
    div[data-testid="stNumberInput"] button:hover {
        background: #3D4460 !important;
        color: #F0F0DB !important;
    }

    /* Selectbox */
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #262B3E !important;
        border: 1px solid #3D4460 !important;
        color: #F0F0DB !important;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
        border-color: #ACBAC4 !important;
    }

    /* Multiselect */
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background: #262B3E !important;
        border: 1px solid #3D4460 !important;
        color: #F0F0DB !important;
    }
    div[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background: #3D4460 !important;
        color: #F0F0DB !important;
    }

    /* Bordered containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #262B3E !important;
        border-color: #3D4460 !important;
        border-radius: 12px !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #ACBAC4 !important;
        box-shadow: 0 4px 20px rgba(172,186,196,0.08) !important;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border: 1px solid #3D4460 !important;
        border-radius: 8px !important;
    }

    /* Divider */
    hr { border-color: #3D4460 !important; }

    /* Alert / info / warning */
    div[data-testid="stAlert"] {
        background: #262B3E !important;
        border: 1px solid #3D4460 !important;
        color: #ACBAC4 !important;
        border-radius: 8px !important;
    }

    /* Status widget */
    div[data-testid="stStatusWidget"] {
        background: #262B3E !important;
        border: 1px solid #3D4460 !important;
    }

    /* Tab bar */
    div[data-testid="stTabs"] button[role="tab"] {
        color: #ACBAC4 !important;
        font-size: 13px !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #F0F0DB !important;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover {
        color: #E1D9BC !important;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       DATA PULL TAB HELPERS
    ══════════════════════════════════════════════════════════════════════════ */
    .section-label {
        font-size: 11px;
        font-weight: 700;
        color: #ACBAC4;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .summary-box {
        background: #262B3E;
        border: 1px solid #3D4460;
        border-radius: 8px;
        padding: 10px 12px;
        font-size: 11px;
        color: #ACBAC4;
        line-height: 1.8;
        margin: 8px 0;
    }
    .summary-box b {
        color: #ACBAC4;
        font-size: 10px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .summary-box .val { color: #F0F0DB; font-weight: 700; }
    .summary-box .dim { color: #5A6080; }

    .hint-text {
        font-size: 11px;
        color: #5A6080;
        line-height: 1.8;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       ARTICLE & REPORT CARDS
    ══════════════════════════════════════════════════════════════════════════ */

    /* Badge — warm sand */
    .art-card-badge {
        display: inline-block;
        background: #E1D9BC;
        color: #30364F;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        padding: 2px 9px;
        border-radius: 20px;
        margin-bottom: 8px;
        width: fit-content;
    }

    /* Title — cream, fixed 3-line height */
    .art-card-title {
        font-size: 15px;
        font-weight: 700;
        color: #F0F0DB;
        line-height: 1.45;
        height: calc(1.45em * 3);
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        margin-bottom: 6px;
    }

    /* Report card desc — fixed 2-line height */
    .rep-card-desc {
        font-size: 12px;
        color: #ACBAC4;
        line-height: 1.55;
        height: calc(1.55em * 2);
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        margin-bottom: 10px;
    }

    /* Meta row */
    .art-card-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 11px;
        color: #ACBAC4;
        border-top: 1px solid #3D4460;
        padding-top: 8px;
        margin-top: 4px;
        margin-bottom: 8px;
    }

    /* Baca / Lihat button inside cards */
    div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #3D4460 !important;
        color: #ACBAC4 !important;
        font-size: 12px !important;
        border-radius: 8px !important;
        transition: border-color 0.2s, color 0.2s !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] button[kind="secondary"]:hover {
        border-color: #E1D9BC !important;
        color: #F0F0DB !important;
        background: transparent !important;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       RESULT PILL & ACTIVE REPORT STRIP
    ══════════════════════════════════════════════════════════════════════════ */
    .result-pill {
        display: inline-block;
        background: #262B3E;
        color: #ACBAC4;
        font-size: 13px;
        font-weight: 600;
        padding: 5px 16px;
        border-radius: 20px;
        border: 1px solid #3D4460;
        margin-bottom: 10px;
    }

    .active-report-strip {
        background: #262B3E;
        border: 1px solid #3D4460;
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .active-report-strip-name {
        font-size: 15px;
        font-weight: 700;
        color: #F0F0DB;
    }
    .active-report-strip-meta {
        font-size: 11px;
        color: #ACBAC4;
    }

    /* ══════════════════════════════════════════════════════════════════════════
       RESULT META & PAGINATION
    ══════════════════════════════════════════════════════════════════════════ */
    .result-meta-row {
        font-size: 11px;
        color: #ACBAC4;
        padding: 4px 0 8px;
    }
    .result-meta-row span { color: #F0F0DB; font-weight: 700; }

    .page-info {
        text-align: center;
        padding-top: 8px;
        color: #ACBAC4;
        font-size: 13px;
    }
    .page-info b { color: #F0F0DB; }
    </style>
    """, unsafe_allow_html=True)


def render_header(db_connected, db_name=""):
    h1, h2, h3 = st.columns([1, 3, 1.2])
    with h1:
        st.markdown(
            "<span style='font-size:22px; font-weight:800; color:#F0F0DB;'>EIU</span>",
            unsafe_allow_html=True
        )
    with h2:
        st.markdown(
            "<h3 style='text-align:center; letter-spacing:3px; color:#ACBAC4; "
            "font-weight:400; opacity:0.8;'>DATA PULL PLATFORM</h3>",
            unsafe_allow_html=True
        )
    with h3:
        if db_connected:
            st.markdown(
                f"<div style='text-align:right'>"
                f"<span style='font-size:12px; color:#E1D9BC;'>🟢 {db_name}</span></div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='text-align:right'>"
                "<span style='font-size:12px; color:#5A6080;'>⚪ Offline</span></div>",
                unsafe_allow_html=True
            )
    st.divider()


def render_section_label(text):
    st.markdown(f'<p class="section-label">{text}</p>', unsafe_allow_html=True)


def render_summary_box(n_ind, n_geo, year_from, year_to):
    ind_val  = f'<span class="val">{n_ind}</span>'  if n_ind > 0 else f'<span class="dim">0</span>'
    geo_val  = f'<span class="val">{n_geo}</span>'  if n_geo > 0 else f'<span class="dim">0</span>'
    year_str = f'<span class="dim">{year_from}–{year_to}</span>'
    st.markdown(
        f'<div class="summary-box"><b>Ringkasan</b><br>'
        f'{ind_val} indikator<br>{geo_val} negara<br>{year_str}</div>',
        unsafe_allow_html=True
    )


def render_hints(n_ind, n_geo):
    hints = []
    if n_ind == 0: hints.append("· Pilih indikator")
    if n_geo == 0: hints.append("· Pilih negara")
    if hints:
        st.markdown(
            '<div class="hint-text">' + "<br>".join(hints) + '</div>',
            unsafe_allow_html=True
        )


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


def toggle_all_global(prefix, nodes, master_key):
    status = st.session_state[master_key]

    def walk(data, path=""):
        for idx, node in enumerate(data):
            name     = node.get("name", "Unknown")
            node_id  = node.get("id")
            cur_path = f"{path}/{name}_{idx}"
            if "children" in node and node["children"]:
                walk(node["children"], cur_path)
            else:
                st.session_state[f"{prefix}_leaf_{node_id}_{cur_path}"] = status

    walk(nodes)


def render_tree(node, level, key_prefix, selected_list, query="", idx=0, path="", parent=""):
    name    = node.get("name", "Unknown")
    node_id = node.get("id")

    if name == parent and "children" in node:
        for i, c in enumerate(node["children"]):
            render_tree(c, level, key_prefix, selected_list, query, i, path, name)
        return

    curr_path = f"{path}/{name}_{idx}"

    if query and query.lower() not in name.lower() and not any(
        query.lower() in str(c).lower() for c in node.get("children", [])
    ):
        return

    if "children" in node and node["children"]:
        with st.expander(name, expanded=bool(query)):
            for i, c in enumerate(node["children"]):
                render_tree(c, level + 1, key_prefix, selected_list, query, i, curr_path, name)
    else:
        if st.checkbox(name, key=f"{key_prefix}_leaf_{node_id}_{curr_path}"):
            selected_list.append(node_id)