import requests
import time
import xml.etree.ElementTree as ET
import re
from services.llm_service import translate_query_for_academic


_query_cache = {}


def search_semantic_scholar(query: str, limit=5) -> list:
    """Tìm kiếm từ Semantic Scholar."""
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,authors,year,abstract,url"
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 429:
            print("[External] Semantic Scholar rate limit hit.")
            return []
            
        response.raise_for_status()
        data = response.json()
        raw_papers = data.get("data", [])
        
        results = []
        for p in raw_papers:
            authors = [a.get("name") for a in p.get("authors", [])]
            results.append({
                "id": p.get("paperId"),
                "title": p.get("title"),
                "authors": authors,
                "year": p.get("year"),
                "abstract": p.get("abstract"),
                "url": p.get("url"),
                "source": "Semantic Scholar",
                "sources": ["semantic_scholar"],
                "is_external": True
            })
        return results
    except Exception as e:
        print(f"[External] Semantic Scholar error: {e}")
        return []

def search_arxiv(query: str, limit=3) -> list:
    """Tìm kiếm từ arXiv (hỗ trợ tốt CNTT/Khoa học máy tính)."""
    try:
        # arXiv API uses atom format (XML)
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={limit}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        results = []
        for entry in root.findall('atom:entry', namespace):
            title = entry.find('atom:title', namespace).text.strip()
            summary = entry.find('atom:summary', namespace).text.strip()
            published = entry.find('atom:published', namespace).text
            year = published.split('-')[0] if published else None
            url_link = entry.find('atom:id', namespace).text
            
            authors = [a.find('atom:name', namespace).text for a in entry.findall('atom:author', namespace)]
            
            results.append({
                "id": url_link.split('/')[-1],
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": summary,
                "url": url_link,
                "source": "arXiv",
                "sources": ["arxiv"],
                "is_external": True
            })
        return results
    except Exception as e:
        print(f"[External] arXiv error: {e}")
        return []

def get_external_academic_papers(query: str, limit=5) -> list:
    """Tổng hợp tài liệu từ nhiều nguồn học thuật quốc tế."""
    if not query or len(query) < 3:
        return []

    # 1. Check Cache
    if query in _query_cache:
        print(f"[External] Cache hit for: {query}")
        return _query_cache[query]

    # Làm sạch query: loại bỏ các hư từ hội thoại
    indicators = [
        "tài liệu", "cuốn sách", "về", "chủ đề", "là", "của", "tìm", "kiếm", "bài báo", 
        "luận văn", "sách", "giáo trình", "lĩnh vực", "cho", "mình", "tôi", "hệ thống",
        "thư viện", "academic", "nội dung", "thuộc", "những", "các"
    ]
    pattern = rf'\b({"|".join(indicators)})\b'
    clean_query = re.sub(pattern, '', query, flags=re.IGNORECASE)
    clean_query = re.sub(r'\s+', ' ', clean_query).strip()
    
    # 1.5 Dịch sang Tiếng Anh để search API quốc tế
    english_query = translate_query_for_academic(clean_query)
    print(f"[External] Translating: '{clean_query}' -> '{english_query}'")
    
    print(f"[External] Researching academic papers for: {english_query}")
    
    # 2. Fetch from multiple sources
    all_results = []
    
    # Semantic Scholar (Priority)
    ss_results = search_semantic_scholar(english_query, limit=limit)
    all_results.extend(ss_results)
    
    # arXiv (Fallback/Supplement)
    if len(all_results) < limit:
        arxiv_results = search_arxiv(english_query, limit=limit - len(all_results))
        all_results.extend(arxiv_results)

    # 2.5 Filter Relevance (Basic)
    # Nếu query có keywords quan trọng, lọc bớt các kết quả External lệch hoàn toàn
    important_keywords = [w for w in english_query.lower().split() if len(w) > 3]
    if important_keywords:
        filtered_external = []
        for p in all_results:
            title_lower = p['title'].lower()
            # Nếu title chứa ít nhất một keyword quan trọng thì giữ lại hoặc nếu query quá ngắn thì giữ
            if any(kw in title_lower for kw in important_keywords) or len(important_keywords) == 0:
                filtered_external.append(p)
            else:
                print(f"[External] Filtering out unrelated paper: {p['title']}")
                continue
        all_results = filtered_external

    # 3. Cache & Return
    _query_cache[query] = all_results[:limit]
    return _query_cache[query]
