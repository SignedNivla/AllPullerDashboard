import streamlit as st
import time
import pandas as pd
from eiu_api import fetch_auto_token, EIUDataAPI
from db_handler import get_engine, push_to_sql
from unctad_api import UNCTADDataAPI
from unctad_catalog import catalog_as_tree, UNCTAD_CATALOG
from config import EIU_EMAIL, EIU_PASSWORD
from ui_components import (
    apply_styles, render_header, render_section_label,
    render_summary_box, render_hints, render_result_meta, render_page_info,
    toggle_all_global, render_tree,
    # Zone A
    render_panel_header, render_right_panel, count_leaves,
    flatten_tree, render_grouped_multiselect, select_all_groups,
    # Zone C
    render_result_strip_header,
    # Zone D
    render_dl_header, render_dl_steps, render_dl_status,
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Kredensial & Config
# ─────────────────────────────────────────────────────────────────────────────
# Credentials loaded from .env via config.py
USER_EMAIL    = EIU_EMAIL
USER_PASSWORD = EIU_PASSWORD
st.set_page_config(page_title="EIU", layout="wide", initial_sidebar_state="collapsed")
apply_styles()

# ─────────────────────────────────────────────────────────────────────────────
# 2. Inisialisasi State
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    'token':             None,
    'results_df':        None,
    'db_connected':      False,
    'db_engine':         None,
    'db_config':         {},
    'show_result_table': False,
    'bulk_art_df':       None,
    'dl_id':             None,
    'dl_status':         None,
    'dl_link':           None,
    'dl_format':         'XLSX',
    # UNCTAD
    'unctad_raw_df':      None,
    'unctad_result_df':   None,
    'unctad_code':        None,
    'unctad_show_table':  False,
    'results_sid':           None,
    'results_has_more':      False,
    'results_next_page':     2,
    'results_yf':            2015,
    'results_yt':            2024,
    # Sync
    'sync_results':      [],
    'sync_meta':         {},
    'sync_page':         1,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

if not st.session_state.token:
    st.session_state.token = fetch_auto_token(USER_EMAIL, USER_PASSWORD)

# ─────────────────────────────────────────────────────────────────────────────
# 3. Dialogs
# ─────────────────────────────────────────────────────────────────────────────
@st.dialog("Database Management")
def db_management_dialog():
    if st.session_state.db_connected:
        st.success(f"Aktif: **{st.session_state.db_config.get('db_name')}**")
        if st.button("Putuskan", use_container_width=True):
            st.session_state.db_connected = False
            st.session_state.db_engine    = None
            st.rerun()
    else:
        db_type = st.selectbox("Tipe", ["PostgreSQL", "MySQL"])
        c1, c2  = st.columns(2)
        with c1:
            host  = st.text_input("Host", "localhost")
            name  = st.text_input("Database Name")
            user  = st.text_input("User")
        with c2:
            port  = st.text_input("Port", "5432" if db_type == "PostgreSQL" else "3306")
            table = st.text_input("Table", "eiu_data")
            pwd   = st.text_input("Password", type="password")
        if st.button("Hubungkan", type="primary", use_container_width=True):
            try:
                engine = get_engine(db_type, user, pwd, host, port, name)
                st.session_state.db_engine    = engine
                st.session_state.db_connected = True
                st.session_state.db_config    = {"db_name": name, "table_default": table}
                st.success("Terhubung!")
                time.sleep(0.8)
                st.rerun()
            except Exception as e:
                st.error(f"Gagal: {e}")


@st.dialog("Push ke Database")
def push_data_dialog(df, show_preview=False):
    """
    show_preview=False  →  ⚡ Push Langsung  — langsung pilih tabel & konfirmasi
    show_preview=True   →  🔍 Preview & Push — tampilkan 50 baris dulu, lalu konfirmasi
    """
    # Meta info
    st.markdown(
        f"**{len(df):,}** baris &nbsp;·&nbsp; **{len(df.columns)}** kolom",
        unsafe_allow_html=True
    )
    tbl = st.text_input(
        "Tabel Tujuan",
        value=st.session_state.db_config.get('table_default', 'eiu_data')
    )

    # Preview section — only when requested
    if show_preview:
        st.caption("50 baris pertama:")
        st.dataframe(df.head(50), use_container_width=True, height=260)

    if st.button("Konfirmasi Push", type="primary", use_container_width=True):
        try:
            with st.spinner(f"Mendorong {len(df):,} baris ke '{tbl}'..."):
                push_to_sql(df, st.session_state.db_engine, tbl)
            st.success(f"✅ {len(df):,} baris berhasil dikirim ke tabel **{tbl}**!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Gagal: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Header + Auth check
# ─────────────────────────────────────────────────────────────────────────────
render_header(st.session_state.db_connected, st.session_state.db_config.get('db_name', ''))

if not st.session_state.token:
    st.error("Authentication Gagal. Cek USER_EMAIL dan USER_PASSWORD.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# 5. API instance + shared reference data (fetched ONCE, reused by all tabs)
# ─────────────────────────────────────────────────────────────────────────────
api     = EIUDataAPI(st.session_state.token)

# ── One-time warm-up: pre-fill all caches on first load ──────────────────────
if 'cache_warmed' not in st.session_state:
    with st.spinner("Memuat data referensi..."):
        api.fetch_reference()
        api.fetch_article_reference()
    st.session_state.cache_warmed = True

art_ref = api.fetch_article_reference() or {}

geo_map = {
    _g["name"]: _g["code"]
    for _reg in art_ref.get("regions", [])
    for _g   in _reg.get("geographies", [])
    if _g.get("name") and _g.get("code")
}

theme_list = sorted({
    t.get("topic1Name")
    for t in art_ref.get("topics", [])
    if t.get("topic1Name")
})

industry_list = sorted({
    i.get("name")
    for i in art_ref.get("industries", [])
    if i.get("name")
})

geo_map_views = {}
for _reg in art_ref.get("regions", []):
    if _reg.get("name") and _reg.get("code"):
        geo_map_views[_reg["name"]] = _reg["code"]
    for _g in _reg.get("geographies", []):
        if _g.get("name") and _g.get("code"):
            geo_map_views[_g["name"]] = _g["code"]

# ─────────────────────────────────────────────────────────────────────────────
# 6. Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_data, tab_article, tab_views, tab_reports, tab_unctad, tab_db = st.tabs([
    "Data Pull", "Artikel", "EIU Views", "Reports", "UNCTAD", "Database"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA PULL
# ═════════════════════════════════════════════════════════════════════════════
with tab_data:
    data_pkg = api.fetch_reference().get('dataPackage', {})
    series_nodes = data_pkg.get('series', [])
    geo_nodes    = data_pkg.get('geographyLocations', [])

    # Totals for the panel count badges (denominator)
    total_ind = count_leaves(series_nodes)
    total_geo = count_leaves(geo_nodes)

    # ─────────────────────────────────────────────────────────────────────────
    # ZONE A — 3-column selector grid
    # ─────────────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns([5, 4, 3], gap="medium")

    s_ids = []
    g_ids = []

    # ── Col 1: Indikator — grouped by top-level category ─────────────────────
    with c1:
        render_panel_header("Indikator", len(s_ids), total_ind)
        sa1, sb1 = st.columns(2, gap="small")
        with sa1:
            if st.button("Pilih Semua", key="ind_sel_all", use_container_width=True):
                select_all_groups(series_nodes, "ind", select=True)
                st.rerun()
        with sb1:
            if st.button("Hapus Semua", key="ind_clr_all", use_container_width=True):
                select_all_groups(series_nodes, "ind", select=False)
                st.rerun()
        qi = st.text_input("qi", key="qi", label_visibility="collapsed",
                           placeholder="🔍  Cari indikator di semua kategori...")
        with st.container(height=380, border=True):
            render_grouped_multiselect(series_nodes, "ind", s_ids, "Indikator", query=qi)

    # ── Col 2: Negara — grouped by region ────────────────────────────────────
    with c2:
        render_panel_header("Negara", len(g_ids), total_geo)
        sg1, sg2 = st.columns(2, gap="small")
        with sg1:
            if st.button("Pilih Semua", key="geo_sel_all", use_container_width=True):
                select_all_groups(geo_nodes, "geo", select=True)
                st.rerun()
        with sg2:
            if st.button("Hapus Semua", key="geo_clr_all", use_container_width=True):
                select_all_groups(geo_nodes, "geo", select=False)
                st.rerun()
        qg = st.text_input("qg", key="qg", label_visibility="collapsed",
                           placeholder="🔍  Cari negara di semua region...")
        with st.container(height=380, border=True):
            render_grouped_multiselect(geo_nodes, "geo", g_ids, "Negara", query=qg)

    # ── Col 3: Rentang + Ringkasan + RUN ─────────────────────────────────────
    with c3:
        st.markdown('<p class="section-label">Rentang Tahun</p>', unsafe_allow_html=True)
        yf = st.number_input("Dari",   min_value=1980, max_value=2026, value=2015,
                             label_visibility="visible")
        yt = st.number_input("Hingga", min_value=1980, max_value=2026, value=2024,
                             label_visibility="visible")

        render_right_panel(len(s_ids), total_ind, len(g_ids), total_geo, yf, yt)

        # ── Series limit gate ─────────────────────────────────────────────────
        over_limit = len(s_ids) >= 100
        can_run    = len(s_ids) > 0 and len(g_ids) > 0 and not over_limit

        if over_limit and len(s_ids) > 0:
            st.warning(f"{len(s_ids)} seri dipilih — melebihi batas 100 per pull. Gunakan Bulk Export di bawah untuk mengunduh semua data.", icon="⚠️")

        if st.button("▶  RUN DATA PULL", type="primary",
                     use_container_width=True, disabled=not can_run):
            with st.status("📡 Memulai Sinkronisasi API EIU...", expanded=True) as status:
                st.write(f"Mengirim permintaan untuk {len(g_ids)} lokasi...")
                res, err = api.execute_search(s_ids, g_ids, yf, yt)
                if res:
                    sid      = res.get("searchId")
                    all_data = res.get("dataPointRecords", [])
                    st.write(f"Halaman 1 berhasil — {len(all_data)} records. Menampilkan...")

                    # ── Flatten & show page 1 immediately ────────────────────
                    def _flatten(data):
                        rows = []
                        for rec in data:
                            for pt in rec.get("points", []):
                                rows.append({
                                    "geographyName": rec.get("geographyName"),
                                    "seriesName":    rec.get("seriesName"),
                                    "unit":          rec.get("unit"),
                                    "year":          pt.get("time", {}).get("year"),
                                    "value":         pt.get("value"),
                                    "status":        pt.get("status"),
                                })
                        return rows

                    rows = _flatten(all_data)
                    df   = pd.DataFrame(rows)
                    if not df.empty:
                        df["year"] = df["year"].astype(int)
                        df = df[df["year"].isin(range(yf, yt + 1))]

                    st.session_state.results_df        = df if not df.empty else None
                    st.session_state.results_sid       = sid
                    st.session_state.results_has_more  = res.get("hasNextPage", False)
                    st.session_state.results_next_page = 2
                    st.session_state.results_yf        = yf
                    st.session_state.results_yt        = yt
                    st.session_state.show_result_table = False

                    if res.get("hasNextPage"):
                        status.update(
                            label=f"✅ Halaman 1 siap ({len(df):,} baris). Ada halaman berikutnya.",
                            state="complete", expanded=False
                        )
                    else:
                        status.update(
                            label=f"✅ Selesai! {len(df):,} baris.",
                            state="complete", expanded=False
                        )
                else:
                    st.error(f"Error API: {err}")
                    status.update(label="❌ Gagal menarik data.", state="error")

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.divider()

    # ─────────────────────────────────────────────────────────────────────────
    # ZONE C+D — 2-col: left = result strip + table, right = bulk export card
    # ─────────────────────────────────────────────────────────────────────────
    # Derive dl phase before entering columns
    if   st.session_state.dl_link:   dl_phase = "ready"
    elif st.session_state.dl_status: dl_phase = "polling"
    elif st.session_state.dl_id:     dl_phase = "requested"
    else:                            dl_phase = "idle"

    dl_can = len(s_ids) > 0 and len(g_ids) > 0

    col_left, col_right = st.columns([7, 3], gap="medium")

    # ── LEFT: result actions + table ─────────────────────────────────────────
    with col_left:
        if st.session_state.results_df is not None:
            df = st.session_state.results_df
            render_result_strip_header(df)

            b1, b2, b3, b4 = st.columns([1, 1.5, 1.7, 2.5], gap="small")
            with b1:
                st.download_button(
                    "⬇ CSV",
                    df.to_csv(index=False).encode("utf-8"),
                    "eiu_data.csv", "text/csv",
                    use_container_width=True
                )
            with b2:
                if st.button("⚡ Push Langsung", type="primary", use_container_width=True):
                    if st.session_state.db_connected:
                        push_data_dialog(df, show_preview=False)
                    else:
                        db_management_dialog()
            with b3:
                if st.button("🔍 Preview & Push", use_container_width=True):
                    if st.session_state.db_connected:
                        push_data_dialog(df, show_preview=True)
                    else:
                        db_management_dialog()
            with b4:
                lbl = "▲ Sembunyikan" if st.session_state.show_result_table else "▼ Tampilkan Tabel"
                if st.button(lbl, use_container_width=True):
                    st.session_state.show_result_table = not st.session_state.show_result_table
                    st.rerun()

            if st.session_state.show_result_table:
                st.dataframe(df, use_container_width=True, height=400)

            # ── Load More ─────────────────────────────────────────────────────
            if st.session_state.results_has_more:
                st.markdown(
                    f"<div style='font-size:12px; color:#ACBAC4; padding:6px 0;'>"
                    f"Menampilkan halaman 1–{st.session_state.results_next_page - 1}. "
                    f"Masih ada data berikutnya.</div>",
                    unsafe_allow_html=True
                )
                if st.button("⬇ Load More", use_container_width=False):
                    with st.spinner(f"Menarik halaman {st.session_state.results_next_page}..."):
                        more = api.fetch_page(
                            st.session_state.results_sid,
                            st.session_state.results_next_page
                        )
                    if more.get("dataPointRecords"):
                        new_rows = []
                        for rec in more["dataPointRecords"]:
                            for pt in rec.get("points", []):
                                new_rows.append({
                                    "geographyName": rec.get("geographyName"),
                                    "seriesName":    rec.get("seriesName"),
                                    "unit":          rec.get("unit"),
                                    "year":          pt.get("time", {}).get("year"),
                                    "value":         pt.get("value"),
                                    "status":        pt.get("status"),
                                })
                        new_df = pd.DataFrame(new_rows)
                        if not new_df.empty:
                            new_df["year"] = new_df["year"].astype(int)
                            new_df = new_df[new_df["year"].isin(
                                range(st.session_state.results_yf,
                                      st.session_state.results_yt + 1)
                            )]
                            st.session_state.results_df = pd.concat(
                                [st.session_state.results_df, new_df], ignore_index=True
                            )
                    st.session_state.results_has_more  = more.get("hasNextPage", False)
                    st.session_state.results_next_page += 1
                    st.rerun()
        else:
            # Placeholder when no results yet
            st.markdown(
                '<div style="padding:20px 0; color:#5A6080; font-size:12px;">'
                'Belum ada hasil. Pilih indikator &amp; negara, lalu klik RUN.</div>',
                unsafe_allow_html=True
            )

    # ── RIGHT: bulk export card ───────────────────────────────────────────────
    with col_right:
        bulk_highlight = over_limit and len(s_ids) > 0
        with st.container(border=True):
            # Card title row — highlighted in sand when over limit
            title_style = "color:#E1D9BC; font-weight:800;" if bulk_highlight else ""
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0;
                        padding-bottom:12px; border-bottom:1px solid #3D4460; margin-bottom:14px;">
                <span class="dl-card-title" style="{title_style}">Bulk Export</span>
                <span class="dl-card-sub">&nbsp;·&nbsp; ~5 menit</span>
                {"&nbsp;<span style='background:#E1D9BC;color:#30364F;font-size:10px;font-weight:700;padding:2px 8px;border-radius:20px;'>GUNAKAN INI</span>" if bulk_highlight else ""}
            </div>
            """, unsafe_allow_html=True)

            # Format toggle
            fmt_cols = st.columns(2, gap="small")
            for fi, fmt in enumerate(["XLSX", "CSV"]):
                with fmt_cols[fi]:
                    btn_type = "primary" if st.session_state.dl_format == fmt else "secondary"
                    if st.button(fmt, key=f"dl_fmt_{fmt}", type=btn_type,
                                 use_container_width=True):
                        st.session_state.dl_format = fmt
                        st.rerun()

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # Step tracker
            render_dl_steps(dl_phase)

            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

            # Status text
            render_dl_status(
                dl_phase,
                st.session_state.dl_id,
                st.session_state.dl_status,
                st.session_state.dl_link,
                st.session_state.dl_format,
                dl_can,
            )

            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

            # Action button — changes per phase
            if dl_phase == "idle":
                if st.button("REQUEST EXPORT", type="primary",
                             use_container_width=True, disabled=not dl_can):
                    with st.spinner("Mengirim request..."):
                        dl_id = api.request_download(s_ids, g_ids, yf, yt,
                                                     fmt=st.session_state.dl_format)
                    if dl_id:
                        st.session_state.dl_id     = dl_id
                        st.session_state.dl_status = None
                        st.session_state.dl_link   = None
                        st.rerun()
                    else:
                        st.error("Gagal. Coba lagi.")

            elif dl_phase == "requested":
                if st.button("POLL STATUS", type="primary", use_container_width=True):
                    with st.spinner("Mengecek status..."):
                        poll = api.poll_download(st.session_state.dl_id)
                    st.session_state.dl_status = poll
                    if poll.get("downloadLink"):
                        st.session_state.dl_link = poll["downloadLink"]
                    st.rerun()

            elif dl_phase == "polling":
                if st.button("POLL LAGI", type="primary", use_container_width=True):
                    with st.spinner("Mengecek status..."):
                        poll = api.poll_download(st.session_state.dl_id)
                    st.session_state.dl_status = poll
                    if poll.get("downloadLink"):
                        st.session_state.dl_link = poll["downloadLink"]
                    st.rerun()

            if dl_phase != "idle":
                if st.button("Reset", use_container_width=True):
                    st.session_state.dl_id     = None
                    st.session_state.dl_status = None
                    st.session_state.dl_link   = None
                    st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — ARTIKEL
# ═════════════════════════════════════════════════════════════════════════════
with tab_article:
    for k, v in [
        ('reading_article_id', None), ('article_list', []),
        ('art_page', 1), ('total_pages', 1), ('art_search_metadata', {}),
    ]:
        if k not in st.session_state: st.session_state[k] = v

    # ── MODE A: READER ────────────────────────────────────────────────────────
    if st.session_state.reading_article_id:
        if st.button("⬅ Kembali ke Daftar"):
            st.session_state.reading_article_id = None
            st.rerun()
        with st.spinner("Membuka laporan..."):
            details = api.fetch_article_details(st.session_state.reading_article_id)
        if details.get("articleAsNinjs"):
            art = details["articleAsNinjs"]
            st.markdown(f"# {art.get('headline', 'No Title')}")
            styled_html = f"""
            <style>
                body {{
                    background-color:#FDFBF7 !important; color:#1A1A1A !important;
                    font-family:'Georgia',serif; font-size:17px;
                    line-height:1.85; padding:48px 64px !important;
                    max-width:780px; margin:0 auto; border-radius:15px;
                }}
                h1,h2,h3,h4 {{ color:#111 !important; margin-top:28px; font-family:'DM Sans',sans-serif; }}
                p {{ margin-bottom:18px; }}
                a {{ color:#E94560 !important; text-decoration:none; }}
                a:hover {{ text-decoration:underline; }}
            </style>
            <body>{art.get('body_html','')}</body>
            """
            st.components.v1.html(styled_html, height=820, scrolling=True)
        else:
            st.error("Gagal memuat konten artikel.")

    # ── MODE B: SUB-TABS ─────────────────────────────────────────────────────
    else:
        sub_search, sub_sync, sub_bulk = st.tabs([
            "🔍  Cari Artikel", "🔄  Sync Artikel", "📥  Bulk Download"
        ])

        # ════════════════════════════════════════════════════════════════════
        # SUB-TAB 1 — Cari Artikel
        # ════════════════════════════════════════════════════════════════════
        with sub_search:
            render_section_label("Filter Intelijen Terpadu")

            f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 2, 1], vertical_alignment="bottom")
            with f1: q_text         = st.text_input("Kata Kunci:", placeholder="GDP, Inflation...", key="art_q")
            with f2: sel_themes     = st.multiselect("Tema:", options=theme_list, placeholder="Pilih tema...")
            with f3: sel_industries = st.multiselect("Industri:", options=industry_list, placeholder="Pilih industri...")
            with f4: sel_geo_names  = st.multiselect("Negara:", options=sorted(geo_map.keys()), placeholder="Pilih negara...")
            with f5:
                st.write("")
                search_clicked = st.button("CARI", type="primary", use_container_width=True)

            if search_clicked:
                g_codes = [geo_map[n] for n in sel_geo_names]
                st.session_state.art_page = 1
                with st.spinner("Mencari artikel..."):
                    res = api.advanced_search_articles(
                        search_string=q_text, geo_codes=g_codes,
                        industries=sel_industries or None,
                        themes=sel_themes or None, page=1
                    )
                st.session_state.article_list        = res.get("results", [])
                st.session_state.total_pages         = res.get("totalPages", 1)
                st.session_state.art_search_metadata = {
                    "q": q_text, "geos": g_codes,
                    "industries": sel_industries, "themes": sel_themes,
                    "total": res.get("totalResults", 0)
                }

            @st.fragment
            def render_article_grid():
                if not st.session_state.article_list:
                    if search_clicked:
                        st.info("Tidak ada hasil ditemukan.")
                    return
                meta = st.session_state.art_search_metadata
                st.markdown(
                    f'<div class="result-pill">📦 {meta.get("total",0):,} laporan ditemukan</div>',
                    unsafe_allow_html=True
                )
                st.write("")
                items = st.session_state.article_list
                for i in range(0, len(items), 3):
                    cols = st.columns(3, gap="medium")
                    for j in range(3):
                        if i + j >= len(items): break
                        item    = items[i + j]
                        summary = item.get("searchResultSummary", item.get("resultSummary", {}))
                        art_id  = summary.get("articleId", "")
                        title   = summary.get("articleTitle", "No Title Available")
                        date    = summary.get("publicationDate", "")[:10]
                        topic   = (item.get("topics") or [{}])[0].get("topic1Name", "")
                        badge   = topic or (meta.get("themes") or ["EIU Report"])[0]
                        with cols[j]:
                            with st.container(border=True):
                                st.markdown(f"""
                                <div class="art-card-badge">{badge}</div>
                                <div class="art-card-title">{title}</div>
                                <div class="art-card-meta">
                                    <span>🗓️ {date}</span>
                                    <span>🆔 {art_id}</span>
                                </div>
                                """, unsafe_allow_html=True)
                                if st.button("Baca", key=f"read_{art_id}_{i+j}", use_container_width=True):
                                    if art_id:
                                        st.session_state.reading_article_id = art_id
                                        st.rerun()
                    st.write("")
                st.divider()
                p1, p2, p3 = st.columns([1, 2, 1])
                with p1:
                    if st.button("⬅️ Sebelumnya",
                                 disabled=(st.session_state.art_page <= 1),
                                 use_container_width=True):
                        st.session_state.art_page -= 1
                        m = st.session_state.art_search_metadata
                        r = api.advanced_search_articles(m["q"], m["geos"], m["industries"],
                                                         m["themes"], page=st.session_state.art_page)
                        st.session_state.article_list = r.get("results", [])
                        st.rerun()
                with p2:
                    render_page_info(st.session_state.art_page, st.session_state.total_pages)
                with p3:
                    if st.button("Berikutnya ➡️",
                                 disabled=(st.session_state.art_page >= st.session_state.total_pages),
                                 use_container_width=True):
                        st.session_state.art_page += 1
                        m = st.session_state.art_search_metadata
                        r = api.advanced_search_articles(m["q"], m["geos"], m["industries"],
                                                         m["themes"], page=st.session_state.art_page)
                        st.session_state.article_list = r.get("results", [])
                        st.rerun()

            render_article_grid()

        # ════════════════════════════════════════════════════════════════════
        # SUB-TAB 2 — Sync Artikel
        # ════════════════════════════════════════════════════════════════════
        with sub_sync:
            render_section_label("Artikel Diperbarui")
            st.caption("Temukan artikel yang diperbarui atau dipublikasikan dalam rentang tanggal tertentu.")
            st.write("")

            sc1, sc2, sc3, sc4 = st.columns([1.5, 1.5, 2, 1], vertical_alignment="bottom")
            with sc1:
                sync_from = st.date_input("Dari Tanggal", key="sync_from",
                                          value=pd.Timestamp.now() - pd.DateOffset(days=30))
            with sc2:
                sync_to   = st.date_input("Sampai Tanggal", key="sync_to",
                                          value=pd.Timestamp.now())
            with sc3:
                sync_geos = st.multiselect("Filter Negara (opsional):",
                                           options=sorted(geo_map.keys()),
                                           placeholder="Semua negara...",
                                           key="sync_geo_sel")
            with sc4:
                sync_sort = st.selectbox("Urut:", ["ModifiedDate", "PublishedDate"],
                                         key="sync_sort")

            sa, sb = st.columns([3, 1], vertical_alignment="bottom")
            with sa:
                sync_clicked = st.button("Cari Artikel Terbaru", type="primary",
                                         use_container_width=True)
            with sb:
                sync_ps = st.selectbox("Per halaman:", [50, 100, 200, 500],
                                       index=1, key="sync_ps")

            if sync_clicked:
                gc_sync = [geo_map[n] for n in sync_geos] if sync_geos else None
                st.session_state.sync_page = 1
                with st.spinner("Mencari..."):
                    r = api.fetch_modified_articles(
                        str(sync_from), str(sync_to), gc_sync, 1, sync_ps, sync_sort
                    )
                st.session_state.sync_results = r.get("results", [])
                st.session_state.sync_meta    = {
                    "from": str(sync_from), "to": str(sync_to),
                    "geo_codes": gc_sync, "sort": sync_sort,
                    "page_size": sync_ps,
                    "total": r.get("totalResults", 0),
                    "totalPages": r.get("totalPages", 1),
                }

            if st.session_state.sync_results:
                smeta = st.session_state.sync_meta
                st.markdown(
                    f'<div class="result-pill">📦 {smeta.get("total",0):,} artikel ditemukan</div>',
                    unsafe_allow_html=True
                )
                st.write("")
                items = st.session_state.sync_results
                for i in range(0, len(items), 3):
                    cols = st.columns(3, gap="medium")
                    for j in range(3):
                        if i + j >= len(items): break
                        item = items[i+j]
                        s    = item.get("resultSummary") or item.get("searchResultSummary") or item
                        aid  = s.get("articleId", "")
                        ttl  = s.get("articleTitle", "No Title")
                        pub  = s.get("publicationDate", "")[:10]
                        mod  = s.get("lastModifiedDate", "")[:10]
                        with cols[j]:
                            with st.container(border=True):
                                st.markdown(
                                    f'<div class="art-card-badge">Updated</div>'
                                    f'<div class="art-card-title">{ttl}</div>'
                                    f'<div class="art-card-meta">'
                                    f'<span>Pub: {pub}</span>'
                                    f'<span>Mod: {mod}</span>'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
                                if st.button("Baca", key=f"sync_r_{aid}_{i+j}",
                                             use_container_width=True):
                                    if aid:
                                        st.session_state.reading_article_id = aid
                                        st.rerun()
                    st.write("")
                st.divider()
                sp1, sp2, sp3 = st.columns([1, 2, 1])
                with sp1:
                    if st.button("⬅️ Sebelumnya", key="sync_prev",
                                 disabled=(st.session_state.sync_page <= 1),
                                 use_container_width=True):
                        st.session_state.sync_page -= 1
                        m = st.session_state.sync_meta
                        r = api.fetch_modified_articles(
                            m["from"], m["to"], m["geo_codes"],
                            st.session_state.sync_page, m["page_size"], m["sort"]
                        )
                        st.session_state.sync_results = r.get("results", [])
                        st.rerun()
                with sp2:
                    render_page_info(st.session_state.sync_page, smeta.get("totalPages", 1))
                with sp3:
                    if st.button("Berikutnya ➡️", key="sync_next",
                                 disabled=(st.session_state.sync_page >= smeta.get("totalPages", 1)),
                                 use_container_width=True):
                        st.session_state.sync_page += 1
                        m = st.session_state.sync_meta
                        r = api.fetch_modified_articles(
                            m["from"], m["to"], m["geo_codes"],
                            st.session_state.sync_page, m["page_size"], m["sort"]
                        )
                        st.session_state.sync_results = r.get("results", [])
                        st.rerun()
            elif sync_clicked:
                st.info("Tidak ada artikel ditemukan untuk rentang tanggal ini.")

        # ════════════════════════════════════════════════════════════════════
        # SUB-TAB 3 — Bulk Download Artikel
        # ════════════════════════════════════════════════════════════════════
        with sub_bulk:

            # ── STEP 1: Pilih Sumber ─────────────────────────────────────────
            st.markdown("""
            <div style='background:#1E2333; border:1px solid #3D4460; border-radius:10px;
                        padding:16px 20px; margin-bottom:16px;'>
                <div style='font-size:10px; font-weight:700; color:#ACBAC4;
                            letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;'>
                    Langkah 1 — Pilih Sumber Data
                </div>
                <div style='font-size:13px; color:#F0F0DB;'>
                    Pilih dari mana artikel akan ditarik: berdasarkan <b>pencarian (filter keyword/tema/negara)</b>
                    atau berdasarkan <b>rentang tanggal</b> artikel yang diperbarui.
                </div>
            </div>
            """, unsafe_allow_html=True)

            bulk_source = st.radio(
                "Sumber:",
                options=["🔍  Pencarian (keyword / tema / negara)", "🔄  Rentang Tanggal (artikel diperbarui)"],
                key="bulk_source",
                label_visibility="collapsed",
                horizontal=True,
            )
            is_search_mode = "Pencarian" in bulk_source

            st.write("")

            # ── STEP 2: Isi Filter ───────────────────────────────────────────
            st.markdown("""
            <div style='font-size:10px; font-weight:700; color:#ACBAC4;
                        letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;'>
                Langkah 2 — Isi Filter
            </div>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                if is_search_mode:
                    f1, f2 = st.columns(2, gap="medium")
                    with f1:
                        bq_text     = st.text_input("Kata Kunci:", key="bulk_q",
                                                    placeholder="Contoh: GDP, Trade, Inflation...")
                        bsel_geo    = st.multiselect("Negara:", options=sorted(geo_map.keys()),
                                                     key="bulk_geo", placeholder="Semua negara...")
                    with f2:
                        bsel_themes = st.multiselect("Tema:", options=theme_list,
                                                     key="bulk_themes", placeholder="Semua tema...")
                        bsel_ind    = st.multiselect("Industri:", options=industry_list,
                                                     key="bulk_ind", placeholder="Semua industri...")
                    # Placeholders for date mode vars
                    bdate_from = pd.Timestamp.now() - pd.DateOffset(days=30)
                    bdate_to   = pd.Timestamp.now()
                    bsync_geos = []
                else:
                    d1, d2, d3 = st.columns([2, 2, 3], gap="medium")
                    with d1:
                        bdate_from = st.date_input("Dari Tanggal:", key="bulk_date_from",
                                                   value=pd.Timestamp.now() - pd.DateOffset(days=30))
                    with d2:
                        bdate_to   = st.date_input("Sampai Tanggal:", key="bulk_date_to",
                                                   value=pd.Timestamp.now())
                    with d3:
                        bsync_geos = st.multiselect("Filter Negara:", options=sorted(geo_map.keys()),
                                                    key="bulk_sync_geo", placeholder="Semua negara...")
                    # Placeholders for search mode vars
                    bq_text = ""; bsel_geo = []; bsel_themes = []; bsel_ind = []

            st.write("")

            # ── STEP 3: Opsi Pull ────────────────────────────────────────────
            st.markdown("""
            <div style='font-size:10px; font-weight:700; color:#ACBAC4;
                        letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;'>
                Langkah 3 — Opsi Pull
            </div>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                op1, op2 = st.columns([2, 3], gap="medium")
                with op1:
                    bulk_max = st.number_input(
                        "Maksimum artikel:", min_value=10, max_value=10000,
                        value=100, step=20, key="bulk_max",
                        help="Jumlah maksimum artikel yang akan ditarik."
                    )
                with op2:
                    fetch_full = st.toggle(
                        "Ambil konten penuh (body text)",
                        value=False, key="bulk_fetch_full",
                    )
                    if fetch_full:
                        st.caption("⚠️ Lebih lambat — 1 request tambahan per artikel untuk mengambil isi lengkap.")
                    else:
                        st.caption("✅ Cepat — hanya metadata (judul, tanggal, abstrak, URL).")

            st.write("")

            # ── STEP 4: Jalankan ────────────────────────────────────────────
            st.markdown("""
            <div style='font-size:10px; font-weight:700; color:#ACBAC4;
                        letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;'>
                Langkah 4 — Jalankan
            </div>
            """, unsafe_allow_html=True)

            bulk_btn = st.button(
                "▶  MULAI BULK DOWNLOAD",
                type="primary", use_container_width=True, key="bulk_run"
            )

            # ── Pull logic ────────────────────────────────────────────────────
            def _collect_articles_search(max_articles):
                g_codes   = [geo_map[n] for n in bsel_geo]
                collected = []
                page = 1
                while len(collected) < max_articles:
                    res = api.advanced_search_articles(
                        search_string=bq_text, geo_codes=g_codes,
                        industries=bsel_ind or None, themes=bsel_themes or None, page=page,
                    )
                    items = res.get("results", [])
                    if not items: break
                    collected.extend(items)
                    if page >= res.get("totalPages", 1): break
                    page += 1
                return collected[:max_articles]

            def _collect_articles_sync(max_articles):
                gc_sync   = [geo_map[n] for n in bsync_geos] if bsync_geos else None
                collected = []
                page = 1
                while len(collected) < max_articles:
                    res = api.fetch_modified_articles(
                        str(bdate_from), str(bdate_to), gc_sync, page, 100, "ModifiedDate"
                    )
                    items = res.get("results", [])
                    if not items: break
                    collected.extend(items)
                    if page >= res.get("totalPages", 1): break
                    page += 1
                return collected[:max_articles]

            def _extract_meta(item):
                s = item.get("searchResultSummary") or item.get("resultSummary") or item
                return {
                    "articleId":        s.get("articleId", ""),
                    "articleTitle":     s.get("articleTitle", ""),
                    "publicationDate":  s.get("publicationDate", "")[:10],
                    "lastModifiedDate": s.get("lastModifiedDate", "")[:10],
                    "abstract":         s.get("abstract", ""),
                    "viewpointUrl":     s.get("viewpointUrl", ""),
                    "apiUrl":           s.get("apiUrl", ""),
                }

            def _strip_html(html):
                import re
                return re.sub(r"<[^>]+>", " ", html).strip() if html else ""

            def _fetch_one(art_id, hdrs):
                """Fetch headline + body_text for one article."""
                import time as _time
                for attempt in range(3):
                    try:
                        res = api.fetch_article_details(art_id)
                        ninjs = res.get("articleAsNinjs", {})
                        return {
                            "headline":  ninjs.get("headline", ""),
                            "body_text": _strip_html(ninjs.get("body_html", "")),
                        }
                    except Exception:
                        _time.sleep(1)
                return {"headline": "", "body_text": ""}

            def _run_bulk_pull(items, fetch_full_content, source_label):
                from concurrent.futures import ThreadPoolExecutor, as_completed
                total  = len(items)
                metas  = [_extract_meta(it) for it in items]
                rows   = [None] * total
                bar    = st.progress(0, text=f"Memproses 0/{total} artikel...")
                done   = 0

                if fetch_full_content:
                    N_WORKERS = 15
                    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
                        fut_map = {
                            ex.submit(_fetch_one, metas[i]["articleId"], None): i
                            for i in range(total) if metas[i]["articleId"]
                        }
                        for fut in as_completed(fut_map):
                            i       = fut_map[fut]
                            content = fut.result()
                            rows[i] = {**metas[i], **content, "source_pull": source_label}
                            done   += 1
                            bar.progress(done / total,
                                text=f"[{done}/{total}] {rows[i].get('articleTitle','')[:55]}...")
                    # fill skipped
                    for i in range(total):
                        if rows[i] is None:
                            rows[i] = {**metas[i], "headline": "", "body_text": "",
                                       "source_pull": source_label}
                else:
                    for i, meta in enumerate(metas):
                        rows[i] = {**meta, "source_pull": source_label}
                        done += 1
                        bar.progress(done / total,
                            text=f"[{done}/{total}] {meta.get('articleTitle','')[:55]}...")

                bar.empty()
                df = pd.DataFrame(rows)
                # Keep only target columns if full content fetched
                target_cols = ["articleId", "articleTitle", "publicationDate",
                               "headline", "body_text", "source_pull"]
                keep = [c for c in target_cols if c in df.columns]
                return df[keep]

            if bulk_btn:
                with st.status("📡 Menjalankan Bulk Download...", expanded=True) as bstatus:
                    if is_search_mode:
                        st.write("Mengambil daftar artikel dari pencarian...")
                        items = _collect_articles_search(bulk_max)
                        src_label = "search"
                    else:
                        st.write("Mengambil daftar artikel dari rentang tanggal...")
                        items = _collect_articles_sync(bulk_max)
                        src_label = "modified"

                    if not items:
                        bstatus.update(label="⚠️ Tidak ada artikel ditemukan.", state="error")
                    else:
                        st.write(f"✅ {len(items)} artikel ditemukan. Memproses...")
                        df_bulk = _run_bulk_pull(items, fetch_full, src_label)
                        st.session_state["bulk_art_df"] = df_bulk
                        bstatus.update(
                            label=f"✅ Selesai — {len(df_bulk):,} artikel berhasil diunduh.",
                            state="complete", expanded=False,
                        )

            # ── STEP 5: Hasil ────────────────────────────────────────────────
            if st.session_state.get("bulk_art_df") is not None:
                st.divider()
                df_bulk = st.session_state["bulk_art_df"]

                st.markdown("""
                <div style='font-size:10px; font-weight:700; color:#ACBAC4;
                            letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;'>
                    Langkah 5 — Simpan / Export Hasil
                </div>
                """, unsafe_allow_html=True)

                ba1, ba2, ba3 = st.columns(3, gap="small")
                with ba1:
                    st.download_button(
                        "⬇ Download CSV",
                        df_bulk.to_csv(index=False).encode("utf-8"),
                        "eiu_articles_bulk.csv", "text/csv",
                        use_container_width=True, type="primary",
                    )
                with ba2:
                    if st.button("⚡ Push ke Database", use_container_width=True,
                                 key="bulk_push_db"):
                        if st.session_state.db_connected:
                            push_data_dialog(df_bulk, show_preview=False)
                        else:
                            db_management_dialog()
                with ba3:
                    if st.button("🔍 Preview & Push", use_container_width=True,
                                 key="bulk_preview_push"):
                        if st.session_state.db_connected:
                            push_data_dialog(df_bulk, show_preview=True)
                        else:
                            db_management_dialog()

                st.markdown(
                    f"<div style='font-size:11px; color:#5A6080; padding:6px 0;'>"
                    f"<b style='color:#F0F0DB;'>{len(df_bulk):,}</b> artikel &nbsp;·&nbsp;"
                    f"<b style='color:#F0F0DB;'>{len(df_bulk.columns)}</b> kolom &nbsp;·&nbsp;"
                    f"{'konten penuh ✓' if 'body_text' in df_bulk.columns else 'metadata saja'}"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.dataframe(df_bulk, use_container_width=True, height=300)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — EIU VIEWS
# ═════════════════════════════════════════════════════════════════════════════
with tab_views:
    render_section_label("Strategic Insight — EIU Views")
    st.caption("Pilih negara untuk melihat ringkasan strategis EIU.")

    if not geo_map_views:
        st.warning("Kamus kode geografi kosong.")
    else:
        sel_name = st.selectbox("Cari lokasi analisis:", options=sorted(geo_map_views.keys()))
        if st.button("Lihat Pandangan Strategis", type="primary"):
            geo_code = geo_map_views[sel_name]
            with st.spinner(f"Menarik data analisis {sel_name}..."):
                views = api.fetch_eiu_views(geo_code)
            if views.get("eiuViews"):
                for item in views["eiuViews"]:
                    st.markdown(f"### {item['metadataName']}")
                    styled_html = f"""
                    <style>
                        body {{ color:#cccccc !important;
                            font-family:'DM Sans',sans-serif; line-height:1.6; }}
                        a {{ color:#aaaaaa !important; text-decoration:underline; }}
                    </style>
                    {item['eiuViewHtml']}
                    """
                    st.components.v1.html(styled_html, height=600, scrolling=True)
            else:
                st.info(f"Belum ada narasi untuk {sel_name}.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — REPORTS
# ═════════════════════════════════════════════════════════════════════════════
with tab_reports:
    for k, v in [
        ('rep_reports_list', []), ('rep_geo_code', None), ('rep_geo_name', ""),
        ('rep_sel_dates', {}), ('rep_active_report', None),
        ('rep_articles', []), ('rep_reading_id', None),
    ]:
        if k not in st.session_state: st.session_state[k] = v

    READER_STYLE = """
    <style>
        body {
            background-color:#FDFBF7 !important; color:#1A1A1A !important;
            font-family:'Georgia',serif; font-size:17px;
            line-height:1.85; padding:48px 64px !important;
            max-width:780px; margin:0 auto; border-radius:15px;
        }
        h1,h2,h3,h4 {{ color:#111 !important; margin-top:28px; font-family:'DM Sans',sans-serif; }}
        p {{ margin-bottom:18px; }}
        a {{ color:#E94560 !important; text-decoration:none; }}
        a:hover {{ text-decoration:underline; }}
    </style>
    """

    # ── MODE C: READER ─────────────────────────────────────────────────────────
    if st.session_state.rep_reading_id:
        if st.button("⬅ Kembali ke Artikel"):
            st.session_state.rep_reading_id = None
            st.rerun()
        with st.spinner("Membuka artikel..."):
            detail = api.fetch_article_details(st.session_state.rep_reading_id)
        ninjs = detail.get("articleAsNinjs", {})
        st.markdown(f"# {ninjs.get('headline','No Title')}")
        body = ninjs.get("body_html", "")
        if body:
            st.components.v1.html(
                READER_STYLE + f"<body>{body}</body>",
                height=820, scrolling=True
            )
        else:
            st.info("Konten artikel tidak tersedia.")

    # ── MODE B: ARTICLE GRID ───────────────────────────────────────────────────
    elif st.session_state.rep_active_report:
        report = st.session_state.rep_active_report
        cfg    = report.get("reportConfig", {})
        r_name = cfg.get("displayName", "Report")
        r_code = cfg.get("reportCode", "")
        r_date = st.session_state.rep_sel_dates.get(r_code, "")

        if st.button("⬅ Kembali ke Reports"):
            st.session_state.rep_active_report = None
            st.session_state.rep_articles      = []
            st.rerun()

        st.markdown(f"""
        <div class="active-report-strip">
            <div class="art-card-badge">EIU Report</div>
            <div class="active-report-strip-name">{r_name}</div>
            <div class="active-report-strip-meta">
                🗓️ {r_date} &nbsp;·&nbsp; {st.session_state.rep_geo_name}
            </div>
        </div>
        """, unsafe_allow_html=True)

        @st.fragment
        def render_report_article_grid():
            articles = st.session_state.rep_articles
            if not articles:
                st.info("Tidak ada artikel ditemukan untuk edisi ini.")
                return
            st.markdown(
                f'<div class="result-pill">📦 {len(articles)} artikel ditemukan</div>',
                unsafe_allow_html=True
            )
            st.write("")
            for i in range(0, len(articles), 3):
                cols = st.columns(3, gap="medium")
                for j in range(3):
                    if i + j >= len(articles): break
                    art     = articles[i + j]
                    summary = art.get("searchResultSummary", art.get("resultSummary", art))
                    art_id  = summary.get("articleId",    art.get("articleId", ""))
                    title   = summary.get("articleTitle", art.get("articleTitle", "No Title"))
                    date    = summary.get("publicationDate", art.get("publicationDate", ""))[:10]
                    with cols[j]:
                        with st.container(border=True):
                            st.markdown(f"""
                            <div class="art-card-badge">EIU Report</div>
                            <div class="art-card-title">{title}</div>
                            <div class="art-card-meta">
                                <span>🗓️ {date}</span>
                                <span>🆔 {art_id}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            if st.button("Baca", key=f"rep_read_{art_id}_{i+j}",
                                         use_container_width=True):
                                if art_id:
                                    st.session_state.rep_reading_id = art_id
                                    st.rerun()
                st.write("")

        render_report_article_grid()

    # ── MODE A: REPORT CARD GRID ───────────────────────────────────────────────
    else:
        render_section_label("Featured Reports")
        st.caption("Pilih negara untuk melihat laporan unggulan EIU.")

        if not geo_map:
            st.warning("⚠️ Tidak ada data negara.")
        else:
            r1, r2 = st.columns([3, 1], vertical_alignment="bottom")
            with r1:
                geo_name = st.selectbox("Pilih Negara:", options=sorted(geo_map.keys()),
                                        key="rep_geo_sel")
            with r2:
                load_clicked = st.button("Muat Reports", type="primary",
                                         use_container_width=True)

            if load_clicked:
                geo_code = geo_map[geo_name]
                with st.spinner(f"Mengambil reports untuk {geo_name}..."):
                    st.session_state.rep_reports_list = api.get_featured_reports(geo_code)
                    st.session_state.rep_geo_code     = geo_code
                    st.session_state.rep_geo_name     = geo_name
                    st.session_state.rep_sel_dates    = {}

            @st.fragment
            def render_report_grid():
                if not st.session_state.rep_reports_list:
                    return
                st.markdown(
                    f'<div class="result-pill">📦 {len(st.session_state.rep_reports_list)} '
                    f'reports tersedia — {st.session_state.rep_geo_name}</div>',
                    unsafe_allow_html=True
                )
                st.write("")
                reports = st.session_state.rep_reports_list
                for i in range(0, len(reports), 3):
                    cols = st.columns(3, gap="medium")
                    for j in range(3):
                        if i + j >= len(reports): break
                        report    = reports[i + j]
                        cfg       = report.get("reportConfig", {})
                        dates     = report.get("reportDates", [])
                        r_code    = cfg.get("reportCode", f"r_{i+j}")
                        r_name    = cfg.get("displayName", "Report")
                        r_desc    = cfg.get("description", "")
                        pub_dates = [d["reportDate"] for d in dates if d.get("reportDate")]

                        if r_code not in st.session_state.rep_sel_dates and pub_dates:
                            st.session_state.rep_sel_dates[r_code] = pub_dates[0]

                        with cols[j]:
                            with st.container(border=True):
                                st.markdown(f"""
                                <div class="art-card-badge">EIU Report</div>
                                <div class="art-card-title">{r_name}</div>
                                <div class="rep-card-desc">{r_desc}</div>
                                """, unsafe_allow_html=True)
                                if pub_dates:
                                    chosen = st.selectbox(
                                        "Edisi:", options=pub_dates, index=0,
                                        key=f"rep_date_{r_code}_{i+j}",
                                        label_visibility="collapsed"
                                    )
                                    st.session_state.rep_sel_dates[r_code] = chosen
                                else:
                                    chosen = None
                                    st.caption("Tidak ada edisi tersedia.")

                                if chosen and st.button(
                                    "Lihat Artikel",
                                    key=f"rep_view_{r_code}_{i+j}",
                                    use_container_width=True
                                ):
                                    with st.spinner("Mengambil artikel..."):
                                        articles = api.get_report_articles(
                                            r_code, st.session_state.rep_geo_code, chosen
                                        )
                                    st.session_state.rep_active_report = report
                                    st.session_state.rep_articles      = articles
                                    st.rerun()
                    st.write("")

            render_report_grid()

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5 — UNCTAD
# ═════════════════════════════════════════════════════════════════════════════
with tab_unctad:
    unctad_api  = UNCTADDataAPI()
    unctad_tree = catalog_as_tree()
    total_unctad = sum(
        1 for g in unctad_tree
        for sg in g.get("children", [])
        for _ in sg.get("children", [])
    )

    # ── 3-col layout mirroring EIU Data Pull ─────────────────────────────────
    uc1, uc2, uc3 = st.columns([5, 4, 3], gap="medium")

    sel_unctad = []

    # ── Col 1: Dataset selector ───────────────────────────────────────────────
    with uc1:
        render_panel_header("Dataset UNCTAD", len(sel_unctad), total_unctad)
        usa1, usa2 = st.columns(2, gap="small")
        with usa1:
            if st.button("Pilih Semua", key="unctad_sel_all", use_container_width=True):
                select_all_groups(unctad_tree, "unctad", select=True)
                st.rerun()
        with usa2:
            if st.button("Hapus Semua", key="unctad_clr_all", use_container_width=True):
                select_all_groups(unctad_tree, "unctad", select=False)
                st.rerun()
        with st.container(height=420, border=True):
            render_grouped_multiselect(unctad_tree, "unctad", sel_unctad, "Dataset")

    # ── Col 2: Info panel ─────────────────────────────────────────────────────
    with uc2:
        render_panel_header("Dataset Dipilih", len(sel_unctad), total_unctad)
        with st.container(height=420, border=True):
            if sel_unctad:
                for code in sel_unctad:
                    match = next((d for d in UNCTAD_CATALOG if d["code"] == code), None)
                    if match:
                        st.markdown(
                            f"<div style='padding:6px 8px; margin-bottom:6px; "
                            f"background:#1E2333; border-radius:8px; border:1px solid #3D4460;'>"
                            f"<div style='font-size:11px; color:#ACBAC4;'>{match['group']} › {match['subgroup']}</div>"
                            f"<div style='font-size:13px; color:#F0F0DB; font-weight:600; margin-top:2px;'>{match['name']}</div>"
                            f"<div style='font-size:10px; color:#5A6080; margin-top:2px; font-family:monospace;'>{code}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
            else:
                st.markdown(
                    "<div style='padding:16px; color:#5A6080; font-size:12px;'>"
                    "Belum ada dataset dipilih.</div>",
                    unsafe_allow_html=True
                )

    # ── Col 3: Year filter + Ringkasan + RUN ────────────────────────────────
    with uc3:
        st.markdown('<p class="section-label">Filter & Aksi</p>', unsafe_allow_html=True)

        yf_u = st.number_input("Dari Tahun", min_value=1900, max_value=2030,
                               value=2015, key="unctad_yf")
        yt_u = st.number_input("Hingga Tahun", min_value=1900, max_value=2030,
                               value=2024, key="unctad_yt")

        st.markdown(
            f"<div class='right-card' style='margin-top:10px;'>"
            f"<div class='right-card-label'>RINGKASAN</div>"
            f"<div style='font-size:12px; color:#ACBAC4; margin-top:6px;'>"
            f"<b style='color:#F0F0DB'>{len(sel_unctad)}</b> dataset dipilih<br>"
            f"<b style='color:#F0F0DB'>{yf_u}–{yt_u}</b> tahun"
            f"</div></div>",
            unsafe_allow_html=True
        )

        can_pull = len(sel_unctad) > 0
        if st.button("▶  PULL UNCTAD", type="primary",
                     use_container_width=True, disabled=not can_pull):
            frames = []
            errors = {}

            with st.status(
                f"📡 Menarik {len(sel_unctad)} dataset...", expanded=True
            ) as status:
                for i, code in enumerate(sel_unctad, 1):
                    match = next((d for d in UNCTAD_CATALOG if d["code"] == code), None)
                    name  = match["name"] if match else code
                    st.write(f"[{i}/{len(sel_unctad)}] {name}...")

                    df_raw, err = unctad_api.fetch_dataset(code)
                    if err:
                        errors[code] = err
                        st.write(f"  ❌ Gagal: {err}")
                        continue

                    filtered = unctad_api.filter_dataframe(
                        df_raw, year_from=yf_u, year_to=yt_u
                    )
                    # Tag each row with its source dataset code + name
                    filtered.insert(0, "dataset_name", name)
                    filtered.insert(1, "dataset_code", code)
                    frames.append(filtered)
                    st.write(f"  ✅ {len(filtered):,} baris")

                ok   = len(frames)
                fail = len(errors)

                if frames:
                    # Merge all into one DataFrame
                    merged = pd.concat(frames, ignore_index=True)
                    st.session_state.unctad_result_df  = merged
                    st.session_state.unctad_show_table = False
                    st.write(f"  📊 Total gabungan: {len(merged):,} baris dari {ok} dataset")

                status.update(
                    label=f"✅ Selesai — {ok}/{len(sel_unctad)} berhasil, {len(merged):,} baris total"
                          + (f", {fail} gagal" if fail else ""),
                    state="complete" if ok > 0 else "error",
                    expanded=False,
                )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.unctad_result_df is not None:
        st.divider()
        df = st.session_state.unctad_result_df

        # Compact action bar — all in one row
        bar1, bar2, bar3, bar4 = st.columns([1, 1.5, 1.5, 2], gap="small")
        with bar1:
            st.download_button(
                "⬇ CSV", df.to_csv(index=False).encode("utf-8"),
                "unctad_data.csv", "text/csv",
                use_container_width=True,
            )
        with bar2:
            if st.button("⚡ Push ke DB", type="primary", use_container_width=True):
                if st.session_state.db_connected:
                    push_data_dialog(df, show_preview=False)
                else:
                    db_management_dialog()
        with bar3:
            if st.button("🔍 Preview & Push", use_container_width=True):
                if st.session_state.db_connected:
                    push_data_dialog(df, show_preview=True)
                else:
                    db_management_dialog()
        with bar4:
            lbl = "▲ Sembunyikan Tabel" if st.session_state.unctad_show_table else "▼ Tampilkan Tabel"
            if st.button(lbl, use_container_width=True):
                st.session_state.unctad_show_table = not st.session_state.unctad_show_table
                st.rerun()

        # Info strip
        n_datasets = df["dataset_code"].nunique() if "dataset_code" in df.columns else 1
        st.markdown(
            f"<div style='font-size:11px; color:#5A6080; padding:4px 2px;'>"
            f"<span style='color:#F0F0DB; font-weight:700;'>{len(df):,}</span> baris &nbsp;·&nbsp;"
            f"<span style='color:#F0F0DB; font-weight:700;'>{len(df.columns)}</span> kolom &nbsp;·&nbsp;"
            f"<span style='color:#ACBAC4;'>{n_datasets} dataset digabung</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        if st.session_state.unctad_show_table:
            st.dataframe(df, use_container_width=True, height=420)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 6 — DATABASE
# ═════════════════════════════════════════════════════════════════════════════
with tab_db:
    render_section_label("Database Configuration")
    if st.session_state.db_connected:
        st.success(f"🟢 Connected to **{st.session_state.db_config.get('db_name')}**")
        if st.button("Disconnect Database"):
            st.session_state.db_connected = False
            st.session_state.db_engine    = None
            st.rerun()
    else:
        st.caption("Database disconnected.")
        if st.button("Open Connection Manager", type="primary"):
            db_management_dialog()