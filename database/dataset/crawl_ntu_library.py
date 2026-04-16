import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

headers = {
    "User-Agent": "Mozilla/5.0"
}

# =========================
# CLEAN TEXT (lọc rác)
# =========================
def clean_text(text):
    if not text:
        return ""

    text = str(text).strip()

    # ❌ bỏ MARC / text rác
    if "MARC" in text or "Tài liệu" in text:
        return ""

    # ❌ quá dài = khả năng là rác
    if len(text) > 300:
        return ""

    return text


# =========================
# PARSE TABLE (CHỈ TAB MÔ TẢ)
# =========================
def parse_metadata(soup):
    data = {}

    # 🔥 chỉ lấy tab "Mô tả"
    tab = soup.find("div", {"id": "tab1"})

    # fallback nếu không có id tab1
    if not tab:
        tab = soup.find("div", class_="tab-content")

    if not tab:
        return data

    rows = tab.select("table tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            key = cols[0].get_text(strip=True)
            value = cols[1].get_text(" ", strip=True)

            value = clean_text(value)

            if not key or not value:
                continue

            if key in data:
                if isinstance(data[key], list):
                    data[key].append(value)
                else:
                    data[key] = [data[key], value]
            else:
                data[key] = value

    return data


# EXTRACT DATA
# =========================
def extract_data(data, url):
    def get(key):
        return clean_text(data.get(key, ""))

    # ===== AUTHOR =====
    authors = []

    for k in data:
        if "Tác giả" in k:
            val = data[k]
            values = val if isinstance(val, list) else [val]

            for v in values:
                v = clean_text(v)

                if not v:
                    continue

                # 🔥 detect role
                if "GVHD" in v:
                    name = v.replace("GVHD", "").replace(":", "").strip()
                    role = "supervisor"

                elif "(dịch)" in v:
                    name = v.replace("(dịch)", "").strip()
                    role = "translator"

                elif "(bs)" in k:
                    name = v
                    role = "contributor"

                else:
                    name = v
                    role = "author"

                if len(name) < 100:
                    authors.append(f"{name}::{role}")

    # ===== SUBJECT =====
    subjects = []

    for k in data:
        if "Thuật ngữ chủ đề" in k:
            val = data[k]
            values = val if isinstance(val, list) else [val]

            for v in values:
                v = clean_text(v)
                if v and len(v) < 100:
                    subjects.append(v)

    # ===== YEAR =====
    publisher_info = get("Thông tin xuất bản")
    year_match = re.search(r"\d{4}", publisher_info)
    year = year_match.group() if year_match else ""

    # 🔥 ===== JOURNAL (THÊM DUY NHẤT PHẦN NÀY) =====
    journal_info = get("Nguồn trích")

    return {
        "url": url,
        "title": get("Nhan đề"),
        "alternative_title": get("Nhan đề khác"),
        "publisher_info": publisher_info,
        "journal_info": journal_info,  # 🔥 thêm dòng này
        "year": year,
        "pages": get("Mô tả vật lý"),
        "ddc": get("DDC"),
        "authors": "|".join(authors),
        "subjects": "|".join(subjects),
    }


# =========================
# CRAWL 1 LINK
# =========================
def crawl_one(url):
    try:
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            print("❌ Status error:", url)
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        data = parse_metadata(soup)

        if not data:
            print("⚠️ Không parse được:", url)

        return extract_data(data, url)

    except Exception as e:
        print("❌ Error:", url, e)
        return None


# =========================
# FIND URL COLUMN
# =========================
def find_url_column(df):
    for col in df.columns:
        sample_values = df[col].astype(str).head(5)

        for val in sample_values:
            if val.startswith("http"):
                return col

    return None


# =========================
# CRAWL CSV
# =========================
def crawl_csv(input_file, output_file, doc_type):
    df = pd.read_csv(input_file)

    url_col = find_url_column(df)

    if url_col is None:
        raise Exception(f"❌ Không tìm thấy cột URL trong file {input_file}")

    print(f"👉 File: {input_file} | Cột URL: {url_col}")

    results = []

    for i, row in df.iterrows():
        url = str(row[url_col]).strip()

        if not url.startswith("http"):
            print(f"⚠️ Skip dòng {i+1}: {url}")
            continue

        print(f"[{i+1}] Crawling: {url}")

        data = crawl_one(url)

        if data:
            data["type"] = doc_type
            results.append(data)

        time.sleep(1)

    pd.DataFrame(results).to_csv(output_file, index=False, encoding="utf-8-sig")
    print("✅ Done:", output_file)


# =========================
# RUN
# =========================

crawl_csv("sách ngoại văn.csv", "output_ngoai_van.csv", "book")
crawl_csv("sách tiếng việt.csv", "output_tieng_viet.csv", "book")
crawl_csv("giáo trình bài giảng.csv", "output_giao_trinh.csv", "book")
crawl_csv("luận văn.csv", "output_luan_van.csv", "thesis")
crawl_csv("bài báo.csv", "output_bai_bao.csv", "article")