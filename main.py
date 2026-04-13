import streamlit as st
import time
import pandas as pd
from eiu_api import fetch_auto_token, EIUDataAPI
from db_handler import get_engine, push_to_sql
from ui_components import (
    apply_styles, render_header, render_section_label,
    render_summary_box, render_hints, render_result_meta, render_page_info,
    toggle_all_global, render_tree
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Kredensial & Config
# ─────────────────────────────────────────────────────────────────────────────
USER_EMAIL    = ""
USER_PASSWORD = ""
st.set_page_config(page_title="EIU", layout="wide", initial_sidebar_state="collapsed")
apply_styles()

# ─────────────────────────────────────────────────────────────────────────────
# 2. Inisialisasi State
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    'token':            None,
    'results_df':       None,
    'db_connected':     False,
    'db_engine':        None,
    'db_config':        {},
    'show_result_table': False,
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
tab_data, tab_article, tab_views, tab_reports, tab_db = st.tabs([
    "Data Pull", "Artikel", "EIU Views", "Reports", "Database"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA PULL
# ═════════════════════════════════════════════════════════════════════════════
with tab_data:
    data_pkg   = api.fetch_reference().get('dataPackage', {})
    s_ids, g_ids = [], []

    c1, c2, c3 = st.columns([3, 2, 1], gap="medium")

    # ── Indikator (wider) ─────────────────────────────────────────────────────
    with c1:
        render_section_label("Indikator")
        qi = st.text_input("Cari indikator...", key="qi",
                           label_visibility="collapsed", placeholder="Cari indikator...")
        st.checkbox("Pilih Semua Indikator", key="m_ind",
                    on_change=toggle_all_global,
                    args=("ind", data_pkg.get('series', []), "m_ind"))
        with st.container(height=390, border=True):
            for i, s in enumerate(data_pkg.get('series', [])):
                render_tree(s, 0, "ind", s_ids, qi, i)

    # ── Negara (narrower) ─────────────────────────────────────────────────────
    with c2:
        render_section_label("Negara")
        qg = st.text_input("Cari negara...", key="qg",
                           label_visibility="collapsed", placeholder="Cari negara...")
        st.checkbox("Pilih Semua Negara", key="m_geo",
                    on_change=toggle_all_global,
                    args=("geo", data_pkg.get('geographyLocations', []), "m_geo"))
        with st.container(height=390, border=True):
            for i, l in enumerate(data_pkg.get('geographyLocations', [])):
                render_tree(l, 0, "geo", g_ids, qg, i)

    # ── Rentang + Run (sidebar) ───────────────────────────────────────────────
    with c3:
        render_section_label("Rentang")
        yf = st.number_input("Dari",   1980, 2026, 2020)
        yt = st.number_input("Hingga", 1980, 2026, 2024)

        render_summary_box(len(s_ids), len(g_ids), yf, yt)
        render_hints(len(s_ids), len(g_ids))

        can_run = len(s_ids) > 0 and len(g_ids) > 0
        if st.button("▶ RUN DATA PULL", type="primary",
                     use_container_width=True, disabled=not can_run):
            with st.status("📡 Memulai Sinkronisasi API EIU...", expanded=True) as status:
                st.write(f"Mengirim permintaan untuk {len(g_ids)} lokasi...")
                res, err = api.execute_search(s_ids, g_ids, yf, yt)
                if res:
                    sid        = res.get('searchId')
                    all_data   = res.get('dataPointRecords', [])
                    page_count = 1
                    st.write(f"Halaman {page_count} berhasil ({len(all_data)} records).")
                    while res.get('hasNextPage'):
                        page_count += 1
                        st.write(f"Menarik halaman {page_count}... ({len(all_data)} records)")
                        res = api.fetch_page(sid, res.get('pageNumber', 1) + 1)
                        if res.get('dataPointRecords'):
                            all_data.extend(res['dataPointRecords'])
                    if all_data:
                        st.write("Memproses ke format tabel...")
                        df = pd.json_normalize(
                            all_data, record_path=['points'],
                            meta=['geographyName', 'seriesName', 'unit']
                        )
                        df['year'] = df['time.year'].astype(int)
                        st.session_state.results_df        = df[df['year'].isin(range(yf, yt + 1))]
                        st.session_state.show_result_table = False
                        status.update(
                            label=f"✅ Selesai! {len(st.session_state.results_df):,} baris.",
                            state="complete", expanded=False
                        )
                    else:
                        status.update(label="⚠️ Tidak ada data ditemukan.", state="error")
                else:
                    st.error(f"Error API: {err}")
                    status.update(label="❌ Gagal menarik data.", state="error")

    # ── Result action bar ─────────────────────────────────────────────────────
    if st.session_state.results_df is not None:
        st.divider()
        df = st.session_state.results_df
        render_result_meta(df)

        b1, b2, b3, b4 = st.columns([1.1, 1.4, 1.4, 4])

        with b1:
            st.download_button(
                "⬇ CSV",
                df.to_csv(index=False).encode("utf-8"),
                "eiu.csv", "text/csv",
                use_container_width=True
            )

        with b2:
            # ⚡ Direct push — no preview, straight to confirm
            if st.button("⚡ Push Langsung", type="primary", use_container_width=True):
                if st.session_state.db_connected:
                    push_data_dialog(df, show_preview=False)
                else:
                    db_management_dialog()

        with b3:
            # 🔍 Preview first, then push
            if st.button("🔍 Preview & Push", use_container_width=True):
                if st.session_state.db_connected:
                    push_data_dialog(df, show_preview=True)
                else:
                    db_management_dialog()

        with b4:
            # Toggle full result table visibility
            lbl = "▲ Sembunyikan Tabel" if st.session_state.show_result_table else "▼ Tampilkan Tabel"
            if st.button(lbl, use_container_width=False):
                st.session_state.show_result_table = not st.session_state.show_result_table
                st.rerun()

        if st.session_state.show_result_table:
            st.dataframe(df, use_container_width=True, height=420)

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

    # ── MODE B: GRID & FILTER ─────────────────────────────────────────────────
    else:
        render_section_label("Filter Intelijen Terpadu")
        f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 2, 1], vertical_alignment="bottom")
        with f1: q_text        = st.text_input("Kata Kunci:", placeholder="GDP, Inflation...", key="art_q")
        with f2: sel_themes    = st.multiselect("Tema:", options=theme_list, placeholder="Pilih tema...")
        with f3: sel_industries= st.multiselect("Industri:", options=industry_list, placeholder="Pilih industri...")
        with f4: sel_geo_names = st.multiselect("Negara:", options=sorted(geo_map.keys()), placeholder="Pilih negara...")
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
                    art_id  = summary.get('articleId', '')
                    title   = summary.get('articleTitle', 'No Title Available')
                    date    = summary.get('publicationDate', '')[:10]
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
                    r = api.advanced_search_articles(m['q'], m['geos'], m['industries'],
                                                     m['themes'], page=st.session_state.art_page)
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
                    r = api.advanced_search_articles(m['q'], m['geos'], m['industries'],
                                                     m['themes'], page=st.session_state.art_page)
                    st.session_state.article_list = r.get("results", [])
                    st.rerun()

        render_article_grid()

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
# TAB 5 — DATABASE
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