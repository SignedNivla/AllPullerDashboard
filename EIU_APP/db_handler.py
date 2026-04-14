import glob
import os
import gc
import polars as pl
import pyarrow.parquet as pq
from sqlalchemy import create_engine, text
import pandas as pd
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
    """Mengirim data ke tabel yang dipilih (Untuk data kecil/menengah)"""
    df.to_sql(table_name, con=engine, if_exists='append', index=False, chunksize=10000, method='multi')

def check_db_rows(engine, table_name):
    """Fungsi verifikasi: Menghitung total baris langsung dari database"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            return count
    except Exception as e:
        return f"Gagal mengecek baris: {e}"

def push_parquet_dir_to_db(staging_dir, engine, table_name="unctad_data"):
    """
    Membaca semua file Parquet di dalam folder staging dan menembakkannya ke DB 
    dengan pemotongan manual (Manual Slicing) agar Progress Bar Streamlit berjalan mulus.
    Dilengkapi dengan verifikasi akhir.
    """
    parquet_files = glob.glob(os.path.join(staging_dir, "*.parquet"))
    
    if not parquet_files:
        st.error("Tidak ada file Parquet ditemukan di folder staging.")
        return

    try:
        # 1. Hitung total baris dari semua file Parquet secara instan (menggunakan metadata)
        total_rows_all_files = sum(pq.read_metadata(f).num_rows for f in parquet_files)
        
        progress_text = f"Memulai transfer {total_rows_all_files:,} baris ke Database..."
        my_bar = st.progress(0, text=progress_text)
        
        total_rows_inserted = 0
        chunk_size = 25000  # Ukuran potong per transaksi (semakin kecil, UI makin sering update)
        
        for file_path in parquet_files:
            # Baca 1 file parquet secara utuh ke RAM (sangat cepat dengan Polars)
            df_polars = pl.read_parquet(file_path)
            rows_in_file = df_polars.height
            
            # 2. Pemotongan Manual (Looping per Chunk)
            for start_idx in range(0, rows_in_file, chunk_size):
                # Ambil potongan data (slice) lalu ubah ke Pandas
                df_chunk = df_polars.slice(start_idx, chunk_size).to_pandas()
                
                # Tembak potongan ini ke DB (method multi sangat penting untuk kecepatan)
                df_chunk.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
                
                # Tambahkan jumlah data yang berhasil masuk
                total_rows_inserted += len(df_chunk)
                
                # 3. Update Progress Bar secara proporsional
                progress_percent = min(total_rows_inserted / total_rows_all_files, 1.0)
                my_bar.progress(
                    progress_percent, 
                    text=f"🚀 Terkirim {total_rows_inserted:,} dari {total_rows_all_files:,} baris..."
                )
            
            # Bersihkan RAM sebelum memuat file Parquet berikutnya
            del df_polars
            gc.collect()
            
        my_bar.empty()
        st.success(f"✅ Proses Transfer Selesai! Mengirim {total_rows_inserted:,} baris.")
        
        # 4. Tahap Verifikasi (Bukti Nyata)
        with st.spinner("Memverifikasi data di dalam Database..."):
            db_count = check_db_rows(engine, table_name)
            if isinstance(db_count, int):
                st.info(f"📊 **Verifikasi Database:** Saat ini terdapat total **{db_count:,} baris** di dalam tabel `{table_name}`.")
            else:
                st.warning(db_count)
        
    except Exception as e:
        st.error(f"❌ Gagal memindahkan data ke database: {e}")