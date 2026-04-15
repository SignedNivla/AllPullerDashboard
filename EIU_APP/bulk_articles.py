import re
import time
import requests
import pandas as pd
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import EIU_API_KEY, EIU_EMAIL, EIU_PASSWORD, EIU_BASE_URL

# CONFIG
N_WORKERS  = 10
PAGE_SIZE  = 20
PAGE_DELAY = 0.5
YEAR_START = 2015
YEAR_END   = datetime.now().year

OUTPUT_FILE = f"articles_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# SESSION
def get_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

session = get_session()

# AUTH
def get_token():
    res = session.post(
        f"{EIU_BASE_URL}/login",
        json={"emailAddress": EIU_EMAIL, "password": EIU_PASSWORD},
        headers={"x-api-key": EIU_API_KEY},
        timeout=15,
    )
    if res.status_code == 200:
        return res.json().get("token")
    print("❌ Login failed:", res.text)
    return None

def make_headers(token):
    return {
        "x-api-key": EIU_API_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

# FETCH
def fetch_window(headers, date_from, date_to, label=""):
    collected = []
    page = 1

    while True:
        payload = {
            "SearchString": "*",  # 🔥 FIX UTAMA
            "PublishedFrom": date_from,
            "PublishedTo": date_to,
            "PageNumber": page,
            "PageSize": PAGE_SIZE,
            "SortBy": "date"
        }

        res = session.post(
            f"{EIU_BASE_URL}/articles/advancedsearch",
            json=payload,
            headers=headers,
            timeout=30,
        )

        if res.status_code == 429:
            time.sleep(10)
            continue

        if res.status_code == 401:
            token = get_token()
            if token:
                headers.update(make_headers(token))
                continue
            break

        if res.status_code != 200:
            print(f"\n❌ {label} Error {res.status_code}: {res.text}")
            print("Payload:", payload)
            break

        data = res.json()
        items = data.get("results", [])
        total_pages = data.get("totalPages", 1)

        if not items:
            break

        for item in items:
            s = item.get("searchResultSummary", item)
            art_id = s.get("articleId")

            if art_id:
                collected.append({
                    "articleId": art_id,
                    "articleTitle": s.get("articleTitle", ""),
                    "publicationDate": (s.get("publicationDate") or "")[:10],
                })

        print(f"{label} page {page}/{total_pages}", end="\r")

        if page >= total_pages:
            break

        page += 1
        time.sleep(PAGE_DELAY)

    return collected

# COLLECT
def collect_all_articles(headers):
    all_data = {}
    print(f"\n📅 Year chunks ({YEAR_START}–{YEAR_END})\n")

    for yr in range(YEAR_START, YEAR_END + 1):
        label = f"[{yr}]"
        rows = fetch_window(headers, f"{yr}-01-01", f"{yr}-12-31", label)

        for r in rows:
            all_data[r["articleId"]] = r

        print(f"{label} → {len(rows)} articles | total: {len(all_data)}")

    return list(all_data.values())

# DETAIL
def fetch_one(meta, headers):
    try:
        res = session.get(
            f"{EIU_BASE_URL}/articles/{meta['articleId']}",
            headers=headers,
            timeout=20
        )

        if res.status_code == 200:
            ninjs = res.json().get("articleAsNinjs", {})
            body = re.sub(r"<[^>]+>", " ", ninjs.get("body_html", ""))

            return {
                **meta,
                "headline": ninjs.get("headline", ""),
                "body_text": body.strip()
            }
    except:
        pass

    return {**meta, "headline": "", "body_text": ""}

# MAIN
def main():
    print("="*60)
    print("EIU Bulk Downloader - FINAL FIX")
    print("="*60)

    token = get_token()
    if not token:
        return

    headers = make_headers(token)

    articles = collect_all_articles(headers)

    if not articles:
        print("❌ No data")
        return

    print(f"\n⚡ Fetching {len(articles)} articles...")

    results = []
    with ThreadPoolExecutor(max_workers=N_WORKERS) as exe:
        futures = [exe.submit(fetch_one, a, headers) for a in articles]

        for i, f in enumerate(as_completed(futures)):
            results.append(f.result())
            print(f"{i+1}/{len(articles)}", end="\r")

    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"\n✅ Saved: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()