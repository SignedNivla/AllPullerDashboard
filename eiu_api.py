import requests
import streamlit as st

API_KEY = ""
BASE_URL = "https://api.eiu.com/v1"
LOGIN_URL = f"{BASE_URL}/login"


def fetch_auto_token(email, password):
    payload = {"emailAddress": email, "password": password}
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    try:
        response = requests.post(LOGIN_URL, json=payload, headers=headers, timeout=10)
        return response.json().get("token") if response.status_code == 200 else None
    except:
        return None


class EIUDataAPI:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "x-api-key": API_KEY,
            "Authorization": f"Bearer {token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }

    # TTL 24 jam — data referensi sangat jarang berubah
    @st.cache_data(ttl=86400)
    def fetch_reference(_self):
        try:
            res = requests.get(f"{BASE_URL}/data/referencedata", headers=_self.headers, timeout=15)
            return res.json() if res.status_code == 200 else {}
        except:
            return {}

    # TTL 30 menit — dipanggil SEKALI di main.py lalu di-share ke semua tab
    @st.cache_data(ttl=1800)
    def fetch_article_reference(_self):
        """Mengambil kamus lengkap: Negara, Topik, Industri. Selalu mengembalikan dict."""
        url = f"{BASE_URL}/articles/referencedata"
        try:
            res = requests.get(url, headers=_self.headers, timeout=15)
            if res.status_code == 200:
                return res.json() or {}
            else:
                st.warning(f"fetch_article_reference gagal: HTTP {res.status_code} — {res.text[:300]}")
                return {}
        except Exception as e:
            st.error(f"fetch_article_reference exception: {e}")
            return {}

    def execute_search(self, s_ids, g_ids, min_yr, max_yr):
        url = f"{BASE_URL}/data/searches"
        payload = {
            "minDate": f"{min_yr}-01-01T00:00:00.000Z",
            "maxDate": f"{max_yr}-12-31T23:59:59.000Z",
            "frequencyType": "Yearly",
            "geographyIds": list(set(g_ids)),
            "seriesIds": list(set(s_ids))
        }
        res = requests.post(url, json=payload, headers=self.headers, timeout=30)
        return (res.json(), None) if res.status_code == 201 else (None, res.text)

    def fetch_page(self, sid, page=1):
        clean_sid = str(sid).replace('"', '').strip()
        res = requests.get(
            f"{BASE_URL}/data/searches/{clean_sid}?page={page}",
            headers=self.headers, timeout=30
        )
        return res.json() if res.status_code == 200 else {}

    # Cache per geo_code, 30 menit
    @st.cache_data(ttl=1800)
    def fetch_eiu_views(_self, geo_code):
        try:
            res = requests.get(f"{BASE_URL}/eiuviews/{geo_code}", headers=_self.headers, timeout=15)
            return (res.json() or {}) if res.status_code == 200 else {}
        except:
            return {}

    # Cache per article_id, 1 jam — artikel tidak berubah
    @st.cache_data(ttl=3600)
    def fetch_article_details(_self, article_id):
        url = f"{BASE_URL}/articles/{article_id}"
        try:
            res = requests.get(url, headers=_self.headers, timeout=15)
            return (res.json() or {}) if res.status_code == 200 else {}
        except:
            return {}

    def advanced_search_articles(self, search_string="", geo_codes=[],
                                  industries=None, themes=None, page=1):
        """Pencarian POST terpadu. Mendukung multi-tema dan multi-industri."""
        url = f"{BASE_URL}/articles/advancedsearch"
        payload = {
            "searchString": search_string,
            "geographyCodes": geo_codes,
            "pageNumber": page,
            "pageSize": 21,
            "sortBy": "Relevance"
        }
        if industries:
            payload["industryFilters"] = [
                {"industryName": ind, "subsectorName": ""}
                for ind in industries
            ]
        if themes:
            payload["topicFilters"] = [
                {"topic1Name": t, "topic2Name": "", "topic3Name": ""}
                for t in themes
            ]
        try:
            res = requests.post(url, json=payload, headers=self.headers, timeout=30)
            return (res.json() or {}) if res.status_code == 200 else {}
        except:
            return {}

    def search_articles_by_theme(self, theme_id, geo_codes=[], page=1):
        url = f"{BASE_URL}/articles/searchesbytheme"
        params = {
            "themeId": theme_id,
            "geographyCodes": ",".join(geo_codes) if geo_codes else None,
            "pageNumber": page,
            "pageSize": 21
        }
        params = {k: v for k, v in params.items() if v is not None}
        try:
            res = requests.get(url, headers=self.headers, params=params, timeout=20)
            return (res.json() or {}) if res.status_code == 200 else {}
        except:
            return {}

    def search_articles_by_report(self, report_name, page=1):
        url = f"{BASE_URL}/articles/searchesbyreport"
        params = {"report": report_name, "pageNumber": page, "pageSize": 21}
        try:
            res = requests.get(url, headers=self.headers, params=params, timeout=20)
            return (res.json() or {}) if res.status_code == 200 else {}
        except:
            return {}

    # Cache per geo_code, 30 menit
    @st.cache_data(ttl=1800)
    def get_featured_reports(_self, geo_code):
        """Mengambil daftar featured reports berdasarkan kode negara."""
        url = f"{BASE_URL}/featuredreports"
        params = {"geographyCode": geo_code}
        try:
            resp = requests.get(url, headers=_self.headers, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("reports", [])
            return []
        except:
            return []

    def get_report_articles(self, report_code, geo_code, pub_date=None):
        """Mengambil daftar artikel dalam sebuah report."""
        url = f"{BASE_URL}/articles/searchesbyreport"
        params = {"reportCode": report_code, "geographyCode": geo_code}
        if pub_date:
            params["reportPublicationDate"] = pub_date
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=15)
            if resp.status_code == 200:
                return resp.json().get("results", [])
            return []
        except:
            return []