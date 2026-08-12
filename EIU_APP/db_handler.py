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

<<<<<<< HEAD
def push_to_sql(df, engine, table_name):
=======
def push_to_sql(df, engine, table_name, if_exists_mode = 'append'):
>>>>>>> 7f8bb242de4482746da4f23b2e39369ce12f6b3e
    """Mengirim data EIU/Artikel dengan pembersihan kolom yang sama"""
    try:
        df_clean = df.copy()
        df_clean.columns = [clean_column_name(c) for c in df_clean.columns]
        
        df_clean.to_sql(
            table_name, 
            con=engine, 
<<<<<<< HEAD
            if_exists='append', 
=======
            if_exists= if_exists_mode, 
>>>>>>> 7f8bb242de4482746da4f23b2e39369ce12f6b3e
            index=False, 
            chunksize=5000,
            method='multi'
        )
<<<<<<< HEAD
        st.success(f"✅ Berhasil mengirim {len(df_clean):,} baris ke `{table_name}`")
    except Exception as e:
        st.error(f"❌ Gagal mengirim ke `{table_name}`. Pesan: {str(e)}")
=======
        st.success(f"Berhasil mengirim {len(df_clean):,} baris ke `{table_name}`")
    except Exception as e:
        st.error(f"Gagal mengirim ke `{table_name}`. Pesan: {str(e)}")
>>>>>>> 7f8bb242de4482746da4f23b2e39369ce12f6b3e

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
        filename = os.path.basename(file_path).replace(".parquet", "")
        dynamic_table_name = f"{table_prefix}_{clean_column_name(filename)}"
        
<<<<<<< HEAD
        st.write(f"📦 Memproses tabel: `{dynamic_table_name}`...")
=======
        st.write(f"Memproses tabel: `{dynamic_table_name}`...")
>>>>>>> 7f8bb242de4482746da4f23b2e39369ce12f6b3e
        
        df_pd = pl.read_parquet(file_path).to_pandas()
        df_pd.columns = [clean_column_name(c) for c in df_pd.columns]
        
        try:
            df_pd.to_sql(
                name=dynamic_table_name,
                con=engine,
<<<<<<< HEAD
                if_exists='replace', # Dataset baru = Tabel baru/Segar
=======
                if_exists='replace',
>>>>>>> 7f8bb242de4482746da4f23b2e39369ce12f6b3e
                index=False,
                chunksize=2000,
                method=None
            )
<<<<<<< HEAD
            st.caption(f"✅ Selesai: {len(df_pd):,} baris masuk ke `{dynamic_table_name}`")
        except Exception as e:
            st.error(f"❌ Gagal di tabel `{dynamic_table_name}`: {e}")

    st.success("🚀 Semua dataset berhasil dikirim ke tabel masing-masing!")
=======
            st.caption(f"Selesai: {len(df_pd):,} baris masuk ke `{dynamic_table_name}`")
        except Exception as e:
            st.error(f"Gagal di tabel `{dynamic_table_name}`: {e}")

    st.success("Semua dataset berhasil dikirim ke tabel masing-masing!")
>>>>>>> 7f8bb242de4482746da4f23b2e39369ce12f6b3e
