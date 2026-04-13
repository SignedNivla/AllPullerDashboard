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

    def filter_dataframe(
        self,
        df:        pd.DataFrame,
        economies: list | None = None,
        year_from: int | None  = None,
        year_to:   int | None  = None,
    ) -> pd.DataFrame:
        result = df.copy()

        if "Year" in result.columns:
            result["Year"] = pd.to_numeric(result["Year"], errors="coerce")
            if year_from:
                result = result[result["Year"] >= year_from]
            if year_to:
                result = result[result["Year"] <= year_to]

        eco_col = None
        for col in ["Economy Label", "Economy", "Reporter Label", "Reporter"]:
            if col in result.columns:
                eco_col = col
                break

        if economies and eco_col:
            result = result[result[eco_col].isin(economies)]

        return result.reset_index(drop=True)

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