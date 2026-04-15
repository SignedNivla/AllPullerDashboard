import glob
import os
import gc
import re
import polars as pl
import pyarrow.parquet as pq
from sqlalchemy import create_engine, text
import streamlit as st

def get_engine(db_type, db_user, db_pass, db_host, db_port, db_name):
    """Membuat koneksi database menggunakan SQLAlchemy"""
    protocol = "postgresql" if db_type == "PostgreSQL" else "mysql+pymysql"
    conn_str = f"{protocol}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(conn_str)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return engine

def push_to_sql(df, engine, table_name):
    """Mengirim data EIU/Artikel dengan pembersihan kolom yang sama"""
    try:
        df_clean = df.copy()
        df_clean.columns = [clean_column_name(c) for c in df_clean.columns]
        
        # Kirim ke SQL
        df_clean.to_sql(
            table_name, 
            con=engine, 
            if_exists='append', 
            index=False, 
            chunksize=5000,
            method='multi'
        )
        st.success(f"✅ Berhasil mengirim {len(df_clean):,} baris ke `{table_name}`")
    except Exception as e:
        # Tampilkan error asli agar kita tahu masalahnya jika bukan kolom
        st.error(f"❌ Gagal mengirim ke `{table_name}`. Pesan: {str(e)}")

def check_db_rows(engine, table_name):
    """Fungsi verifikasi: Menghitung total baris langsung dari database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            return count
    except Exception as e:
        return f"Gagal mengecek baris: {e}"

def clean_column_name(col):
    clean = col.replace('$', 'US')
    clean = re.sub(r'[^a-zA-Z0-9]', '_', clean)
    clean = clean.lower()
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean[:60]

def push_parquet_dir_to_db(staging_dir, engine, table_prefix="unctad"):
    """
    Otomatis membuat tabel berdasarkan Dataset Code yang ada di nama file.
    Contoh: unctad_us_intratrade, unctad_us_merchtotal
    """
    parquet_files = glob.glob(os.path.join(staging_dir, "*.parquet"))
    
    if not parquet_files:
        st.error("Tidak ada file Parquet ditemukan.")
        return
    
    progress_container = st.empty()
    
    for file_path in parquet_files:
        # 1. Ambil Dataset Code dari nama file (misal: unctad_US.IntraTrade.parquet)
        filename = os.path.basename(file_path).replace(".parquet", "")
        # Bersihkan nama agar aman untuk SQL (jadi unctad_us_intratrade)
        dynamic_table_name = f"{table_prefix}_{clean_column_name(filename)}"
        
        st.write(f"📦 Memproses tabel: `{dynamic_table_name}`...")
        
        # 2. Baca data
        df_pd = pl.read_parquet(file_path).to_pandas()
        df_pd.columns = [clean_column_name(c) for c in df_pd.columns]
        
        # 3. Kirim ke DB (Gunakan 'replace' agar skema selalu segar sesuai dataset)
        try:
            df_pd.to_sql(
                name=dynamic_table_name,
                con=engine,
                if_exists='replace', # Dataset baru = Tabel baru/Segar
                index=False,
                chunksize=2000,
                method=None
            )
            st.caption(f"✅ Selesai: {len(df_pd):,} baris masuk ke `{dynamic_table_name}`")
        except Exception as e:
            st.error(f"❌ Gagal di tabel `{dynamic_table_name}`: {e}")

    st.success("🚀 Semua dataset berhasil dikirim ke tabel masing-masing!")