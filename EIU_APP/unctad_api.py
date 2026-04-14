import io
import os
import glob
import time
import hashlib
import tempfile
import requests
import pandas as pd
import py7zr
from config import UNCTAD_CLIENT_ID, UNCTAD_CLIENT_SECRET, UNCTAD_BULK_BASE
import polars as pl

BULK_BASE  = UNCTAD_BULK_BASE
_CACHE_DIR = os.path.join(tempfile.gettempdir(), "unctad_cache")
os.makedirs(_CACHE_DIR, exist_ok=True)


class UNCTADDataAPI:

    def __init__(self):
        self.headers = {
            "ClientId":     UNCTAD_CLIENT_ID,
            "ClientSecret": UNCTAD_CLIENT_SECRET,
        }

    def fetch_dataset(self, code: str) -> tuple:
        """
        Download a UNCTAD bulk dataset by code (e.g. 'US.TradeMerchTotal').
        Returns (DataFrame, None) on success or (None, error_message) on failure.
        Uses disk cache (parquet) to avoid re-downloading within 1 hour.
        No st.cache_data — dataset too large for pickle-based memory cache.
        """
        cache_key  = hashlib.md5(code.encode()).hexdigest()[:12]
        cache_path = os.path.join(_CACHE_DIR, f"unctad_{cache_key}.parquet")

        # Return from disk cache if < 1 hour old
        if os.path.exists(cache_path):
            age = time.time() - os.path.getmtime(cache_path)
            if age < 3600:
                try:
                    return pd.read_parquet(cache_path), None
                except Exception:
                    os.remove(cache_path)  # corrupted — re-download

        url_code = code.replace(".", "_")
        url      = f"{BULK_BASE}/{code}/{url_code}"

        try:
            r = requests.get(url, headers=self.headers, timeout=60)
        except Exception as e:
            return None, f"Request error: {e}"

        if r.status_code != 200:
            try:
                err = r.json().get("Error", r.text[:200])
            except Exception:
                err = r.text[:200]
            return None, f"HTTP {r.status_code}: {err}"

        # Extract CSV from 7z archive
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                with py7zr.SevenZipFile(io.BytesIO(r.content), mode="r") as z:
                    z.extractall(path=tmpdir)

                csv_files = glob.glob(os.path.join(tmpdir, "**", "*.csv"), recursive=True)
                if not csv_files:
                    all_files = [f for f in glob.glob(os.path.join(tmpdir, "**", "*"), recursive=True)
                                 if os.path.isfile(f)]
                    if not all_files:
                        return None, "No files found in archive"
                    csv_files = all_files

                try:
                    # Coba gunakan pyarrow (sangat cepat, butuh pip install pyarrow)
                    df = pd.read_csv(
                        csv_files[0],
                        na_values=["", "NA", "N/A", ".."],
                        encoding="utf-8",
                        engine="pyarrow",      # ⚡ TURBO ENGINE
                        dtype_backend="pyarrow" # ⚡ Tipe data memori efisien
                    )
                except Exception:
                    # Fallback ke cara lama jika pyarrow gagal/tidak ada
                    df = pd.read_csv(
                        csv_files[0],
                        na_values=["", "NA", "N/A", ".."],
                        encoding="utf-8",
                        encoding_errors="replace",
                        low_memory=False,
                    )

            # Save to disk cache
            try:
                df.to_parquet(cache_path, index=False)
            except Exception:
                pass  # non-fatal

            return df, None

        except Exception as e:
            return None, f"Extract error: {e}"
        
    def download_and_extract_only(self, code: str) -> tuple:
        """
        Hanya mengunduh dan mengekstrak file CSV tanpa membacanya ke memori.
        Sangat cocok untuk Polars Lazy Execution.
        Mengembalikan tuple: (path_file_csv, pesan_error)
        """
        # 1. Siapkan folder khusus untuk cache file CSV mentah
        raw_cache_dir = os.path.join(tempfile.gettempdir(), "unctad_raw_csv_cache")
        os.makedirs(raw_cache_dir, exist_ok=True)
        
        cache_key = hashlib.md5(code.encode()).hexdigest()[:12]
        expected_csv_dir = os.path.join(raw_cache_dir, f"raw_{cache_key}")
        os.makedirs(expected_csv_dir, exist_ok=True)
        
        # 2. Cek apakah file CSV sudah pernah diunduh dan diekstrak
        existing_csvs = glob.glob(os.path.join(expected_csv_dir, "**", "*.csv"), recursive=True)
        if existing_csvs:
            # PENTING: Jika sudah ada, langsung kembalikan lokasinya (Sangat menghemat waktu testing!)
            return existing_csvs[0], None 

        # 3. Jika belum ada, lakukan proses unduh API
        url_code = code.replace(".", "_")
        url      = f"{BULK_BASE}/{code}/{url_code}"

        try:
            # Timeout dinaikkan karena file UNCTAD bisa ratusan MB
            r = requests.get(url, headers=self.headers, timeout=300) 
        except Exception as e:
            return None, f"Request error: {e}"

        if r.status_code != 200:
            try:
                err = r.json().get("Error", r.text[:200])
            except Exception:
                err = r.text[:200]
            return None, f"HTTP {r.status_code}: {err}"

        # 4. Ekstrak file biner langsung ke hardisk
        try:
            with py7zr.SevenZipFile(io.BytesIO(r.content), mode="r") as z:
                z.extractall(path=expected_csv_dir)

            # Cari file CSV hasil ekstraksi
            extracted_csvs = glob.glob(os.path.join(expected_csv_dir, "**", "*.csv"), recursive=True)
            if not extracted_csvs:
                return None, "File CSV tidak ditemukan di dalam arsip .7z"
            
            return extracted_csvs[0], None

        except Exception as e:
            return None, f"Extract error: {e}"

    def fetch_and_filter_massive(self, csv_file_path: str, year_from: int, year_to: int) -> pl.DataFrame:
        """
        Membaca dan memfilter CSV Raksasa menggunakan Polars (Sangat Cepat & Hemat RAM).
        """
        try:
            # Menggunakan scan_csv (Lazy Execution) - Sangat hemat RAM
            # Kita paksakan tipe data Year menjadi String dulu agar tidak error jika ada spasi
            q = pl.scan_csv(csv_file_path, infer_schema_length=10000, ignore_errors=True)
            
            # Kita hanya peduli kolom Year
            if "Year" in q.collect_schema().names():
                q = q.with_columns(
                    pl.col("Year").cast(pl.Int32, strict=False)
                ).filter(
                    (pl.col("Year").is_not_null()) & 
                    (pl.col("Year") >= year_from) & 
                    (pl.col("Year") <= year_to)
                )
            
            # Sekarang, kumpulkan datanya (Eksekusi multi-core)
            # Hasil dari 'collect()' ini adalah Polars DataFrame, jauh lebih ringan dari Pandas
            df_filtered = q.collect()
            
            return df_filtered, None
            
        except Exception as e:
            return None, f"Gagal membaca dengan Polars: {e}"

    def filter_dataframe(
        self,
        df:        pd.DataFrame,
        economies: list | None = None,
        year_from: int | None  = None,
        year_to:   int | None  = None,
    ) -> pd.DataFrame:
        result = df

        if "Year" in result.columns:
            result["Year"] = pd.to_numeric(result["Year"], errors="coerce")
            if year_from or year_to:
                # Gunakan query mask yang cepat
                mask = result["Year"].notna()
                if year_from:
                    mask &= (result["Year"] >= year_from)
                if year_to:
                    mask &= (result["Year"] <= year_to)

        eco_col = next((col for col in ["Economy Label", "Economy", "Reporter Label", "Reporter"] 
                        if col in result.columns), None)

        if economies and eco_col:
            result = result[result[eco_col].isin(economies)]

        return result

    def get_economies(self, df: pd.DataFrame) -> list:
        for col in ["Economy Label", "Economy", "Reporter Label", "Reporter"]:
            if col in df.columns:
                return sorted(df[col].dropna().unique().tolist())
        return []

    def get_year_range(self, df: pd.DataFrame) -> tuple:
        if "Year" in df.columns:
            years = pd.to_numeric(df["Year"], errors="coerce").dropna()
            if not years.empty:
                return int(years.min()), int(years.max())
        return 2000, 2024