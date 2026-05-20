import os
import sys
import json
import re
import time

# Reconfigure stdout/stderr to support Vietnamese characters on Windows console
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.neo4j_connection import neo4j_conn
from services.llm_service import get_client

# Define the 8 main academic fields
ACADEMIC_FIELDS = [
    "Công nghệ thông tin & Khoa học máy tính",
    "Kinh tế, Quản trị & Kinh doanh",
    "Kỹ thuật & Sản xuất",
    "Hóa học & Khoa học vật liệu",
    "Y tế, Dược học & Sinh học",
    "Nông nghiệp & Công nghệ thực phẩm",
    "Khoa học Xã hội, Giáo dục & Ngôn ngữ học",
    "Lịch sử, Địa lý & Chính trị"
]

def clean_json_string(text):
    """Clean markdown code block wrappers from JSON string."""
    text = text.strip()
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text

def call_gemini_with_retry(prompt, model="gemini-2.5-flash", temperature=0.2, max_retries=5):
    """Wrapper to call Gemini with exponential backoff retry on rate limits."""
    client = get_client()
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    'temperature': temperature,
                    'max_output_tokens': 4096
                }
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                wait_time = (2 ** attempt) * 5
                print(f"[Warning] Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"[Error] Gemini API Error: {e}")
                time.sleep(2)
    return None

def classify_subjects_batch(subjects):
    """Send a batch of subjects to Gemini for classification into one of the 8 fields."""
    subjects_list_str = json.dumps([{"id": s["id"], "name": s["name"]} for s in subjects], ensure_ascii=False, indent=2)
    
    fields_list_str = "\n".join([f"- {f}" for f in ACADEMIC_FIELDS])
    
    prompt = f"""Bạn là chuyên gia phân loại tài liệu học thuật. Nhiệm vụ của bạn là phân loại các chủ đề (Subject) dưới đây vào một trong 8 Lĩnh vực lớn sau:

{fields_list_str}

Danh sách chủ đề cần phân loại:
{subjects_list_str}

Yêu cầu:
1. Phân loại chính xác, khách quan dựa trên tên chủ đề.
2. Trả về kết quả dưới dạng JSON object thô, trong đó key là Subject ID (ví dụ: "S1") và value là tên Lĩnh vực chính xác (ví dụ: "Nông nghiệp & Công nghệ thực phẩm").
3. Trả về DUY NHẤT mã JSON thô, không viết thêm bất kỳ giải thích, nhận xét hay ký tự markdown nào ngoài khối mã json.

Kết quả JSON:"""

    response_text = call_gemini_with_retry(prompt, temperature=0.1)
    if not response_text:
        return {}
    
    try:
        cleaned_text = clean_json_string(response_text)
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"[Warning] JSON parse failed, trying direct regex extraction for classification batch: {e}")
        try:
            matches = re.findall(r'"(S\d+)"\s*:\s*"([^"]+)"', response_text)
            if matches:
                return {k: v for k, v in matches}
        except:
            pass
        return {}

def suggest_relationships_for_field(field_name, subjects):
    """Ask Gemini to suggest logical RELATED_TO relationships among subjects in the same field."""
    if len(subjects) <= 1:
        return []
    
    subjects_list_str = json.dumps([{"id": s["id"], "name": s["name"]} for s in subjects], ensure_ascii=False, indent=2)
    
    prompt = f"""Bạn là một thủ thư hệ thống và chuyên gia xây dựng đồ thị tri thức (Knowledge Graph).
Chúng ta có danh sách các chủ đề (Subject) thuộc lĩnh vực '{field_name}' như sau:
{subjects_list_str}

Nhiệm vụ của bạn:
1. Tìm và gợi ý các cặp chủ đề có mối liên hệ mật thiết, logic nhất để liên kết với nhau bằng quan hệ [RELATED_TO].
2. Quy tắc liên kết:
   - Chỉ liên kết những chủ đề có liên hệ thực tế, ví dụ: 'Artificial intelligence' và 'Machine learning', hoặc 'Tục ngữ Việt Nam' và 'Ca dao Việt Nam'.
   - Một chủ đề KHÔNG nên liên kết quá nhiều (chỉ khoảng 2-3 mối quan hệ liên kết có ý nghĩa nhất).
   - Hãy chắc chắn kết nối tạo thành các nhóm logic sinh động thay vì nối đại trà hoặc rời rạc cô lập.
3. Trả về kết quả DUY NHẤT dưới dạng JSON array của các cặp ID chủ đề, ví dụ: [["S74", "S76"], ["S93", "S94"]].
4. Tuyệt đối không thêm giải thích hay định dạng markdown bên ngoài khối JSON.

Gợi ý liên kết JSON:"""

    response_text = call_gemini_with_retry(prompt, temperature=0.2)
    if not response_text:
        return []
    
    try:
        cleaned_text = clean_json_string(response_text)
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"[Warning] JSON parse failed, trying direct regex extraction for relationship suggestions: {e}")
        try:
            matches = re.findall(r'\[\s*"(S\d+)"\s*,\s*"(S\d+)"\s*\]', response_text)
            if matches:
                return [list(m) for m in matches]
        except:
            pass
        return []

def run_migration():
    print("=== BẮT ĐẦU DI CHUYỂN & TỔ CHỨC LẠI CHỦ ĐỀ NEO4J ===")
    
    # 1. Fetch all subjects
    print("\n[Bước 1] Đang lấy danh sách chủ đề từ Neo4j...")
    subjects_query = "MATCH (s:Subject) RETURN s.id AS id, s.name AS name, s.field AS field"
    subjects = neo4j_conn.query(subjects_query)
    total_subjects = len(subjects)
    print(f"-> Đã tìm thấy {total_subjects} chủ đề.")
    
    if total_subjects == 0:
        print("[Error] Không tìm thấy chủ đề nào trong database. Hủy di chuyển.")
        return
        
    # 2. Create Field nodes
    print("\n[Bước 2] Khởi tạo các nút Lĩnh vực (:Field) lớn...")
    for idx, field in enumerate(ACADEMIC_FIELDS, 1):
        field_query = """
        MERGE (f:Field {name: $name})
        ON CREATE SET f.id = $id
        RETURN f
        """
        neo4j_conn.query(field_query, {"name": field, "id": f"F{idx}"})
    print("-> Đã khởi tạo thành công 8 Lĩnh vực chính trong Neo4j.")

    # 3. Batch Classify Subjects using Gemini (Incremental)
    print("\n[Bước 3] Phân loại chủ đề vào các lĩnh vực học thuật lớn bằng Gemini AI (Chạy cuốn chiếu)...")
    classifications = {}
    
    # Populate existing classifications from Neo4j
    for s in subjects:
        if s.get("field"):
            classifications[s["id"]] = s["field"]
            
    unclassified_subjects = [s for s in subjects if not s.get("field")]
    total_unclassified = len(unclassified_subjects)
    print(f"-> Có {total_subjects - total_unclassified} chủ đề đã được phân loại trước đó. Cần phân loại mới {total_unclassified} chủ đề.")

    # Skip classification in this run to focus on relationship generation
    total_unclassified = 0

    if total_unclassified > 0:
        batch_size = 15
        for i in range(0, total_unclassified, batch_size):
            batch = unclassified_subjects[i:i+batch_size]
            print(f"  Phân loại lô {i // batch_size + 1}/{(total_unclassified + batch_size - 1) // batch_size} (Chủ đề {i+1} đến {min(i+batch_size, total_unclassified)})...")
            batch_results = classify_subjects_batch(batch)
            classifications.update(batch_results)
            time.sleep(1) # Small throttle
            
    print(f"-> Hoàn thành phân loại. Tổng số đã phân loại trong bộ nhớ: {len(classifications)}/{total_subjects}")

    # 4. Clean up old RELATED_TO relationships
    print("\n[Bước 4] Bỏ qua xóa sạch toàn bộ liên kết (chỉ xóa cuốn chiếu theo từng lĩnh vực cần liên kết mới)...")

    # 5. Save classifications to DB and link Subjects to Fields
    print("\n[Bước 5] Lưu lĩnh vực và tạo quan hệ BELONGS_TO tới Field tương ứng...")
    count_linked = 0
    subjects_by_field = {field: [] for field in ACADEMIC_FIELDS}
    subjects_by_field["Uncategorized"] = []
    
    for s in subjects:
        s_id = s["id"]
        
        # Get classified field, make sure it is in our standard list
        field = classifications.get(s_id)
        if field not in ACADEMIC_FIELDS:
            # Try to match fuzzy or place in Uncategorized
            matched = False
            for f in ACADEMIC_FIELDS:
                if field and (f.lower() in field.lower() or field.lower() in f.lower()):
                    field = f
                    matched = True
                    break
            if not matched:
                field = "Uncategorized"
                
        if field != "Uncategorized":
            subjects_by_field[field].append(s)
            
            # Update Node & Create relation (only if not already linked to avoid redundant query)
            if not s.get("field") or s.get("field") != field:
                update_query = """
                MATCH (s:Subject {id: $id})
                SET s.field = $field
                WITH s
                MERGE (f:Field {name: $field})
                MERGE (s)-[:BELONGS_TO]->(f)
                RETURN count(s) AS updated
                """
                neo4j_conn.query(update_query, {"id": s_id, "field": field})
                count_linked += 1
        else:
            subjects_by_field["Uncategorized"].append(s)
            if s.get("field"):
                # Just set field to null and delete relationships if any
                update_query = """
                MATCH (s:Subject {id: $id})
                SET s.field = null
                WITH s
                OPTIONAL MATCH (s)-[r:BELONGS_TO]->(:Field)
                DELETE r
                """
                neo4j_conn.query(update_query, {"id": s_id})

    print(f"-> Đã đồng bộ thuộc tính field và tạo quan hệ BELONGS_TO thành công thêm cho {count_linked} chủ đề mới.")
    
    # Read actual counts from DB to be absolutely sure
    total_belongs_to = neo4j_conn.query("MATCH (:Subject)-[r:BELONGS_TO]->(:Field) RETURN count(r) AS count")[0]["count"]
    print(f"-> Tổng số liên kết (Subject)-[:BELONGS_TO]->(Field) hiện tại trong DB: {total_belongs_to}")

    # 6. Generate and save logical RELATED_TO relationships inside each Field
    print("\n[Bước 6] Tạo liên kết RELATED_TO logic trong từng lĩnh vực bằng Gemini AI...")
    total_new_rels = 0
    
    for field_name, field_subjects in subjects_by_field.items():
        if field_name == "Uncategorized" or len(field_subjects) <= 1:
            continue
            
        # Kiểm tra xem lĩnh vực này đã có quan hệ RELATED_TO chưa
        check_rel_query = """
        MATCH (s1:Subject {field: $field})-[:RELATED_TO]->(s2:Subject)
        RETURN count(*) AS count
        """
        rel_check = neo4j_conn.query(check_rel_query, {"field": field_name})
        has_existing_rels = rel_check[0]["count"] > 0 if (rel_check and rel_check[0]["count"] > 0) else False
        
        if has_existing_rels:
            print(f"  Lĩnh vực '{field_name}' đã có sẵn {rel_check[0]['count']} quan hệ logic. Bỏ qua để bảo vệ dữ liệu.")
            continue
            
        # Split subjects of this field into subgroups of max 15
        subgroups = [field_subjects[i:i+15] for i in range(0, len(field_subjects), 15)]
        print(f"  Đang phân tích mối quan hệ cho lĩnh vực cần bổ sung: {field_name} (Tổng {len(field_subjects)} chủ đề, chia làm {len(subgroups)} phân nhóm nhỏ)...")
        
        # Delete old relationships in this specific field if any (just to be safe) before saving new ones
        delete_field_rels_query = """
        MATCH (s1:Subject {field: $field})-[r:RELATED_TO]-(s2:Subject {field: $field})
        DELETE r
        """
        neo4j_conn.query(delete_field_rels_query, {"field": field_name})
        
        field_rels_count = 0
        
        for idx, subgroup in enumerate(subgroups, 1):
            print(f"    Phân tích phân nhóm {idx}/{len(subgroups)} ({len(subgroup)} chủ đề)...")
            suggested_pairs = suggest_relationships_for_field(field_name, subgroup)
            print(f"      -> Phân nhóm {idx} có {len(suggested_pairs)} cặp liên kết từ Gemini.")
            
            if not suggested_pairs:
                time.sleep(2)
                continue
                
            for pair in suggested_pairs:
                if not isinstance(pair, list) or len(pair) < 2:
                    continue
                id1, id2 = pair[0], pair[1]
                
                # Ensure both IDs exist in our subgroup subjects to prevent cross-field linkage
                subgroup_ids = {sub["id"] for sub in subgroup}
                if id1 in subgroup_ids and id2 in subgroup_ids and id1 != id2:
                    # Merge relationship (directed s1->s2)
                    relate_query = """
                    MATCH (s1:Subject {id: $id1}), (s2:Subject {id: $id2})
                    MERGE (s1)-[:RELATED_TO]->(s2)
                    RETURN count(*) AS created
                    """
                    neo4j_conn.query(relate_query, {"id1": id1, "id2": id2})
                    field_rels_count += 1
                    total_new_rels += 1
            
            time.sleep(2) # Small throttle
            
        print(f"    -> Lĩnh vực '{field_name}': Đã thiết lập thành công tổng cộng {field_rels_count} liên kết RELATED_TO mới.")
        
    print(f"\n-> TẤT CẢ HOÀN TẤT! Đã hoàn thiện cấu trúc các mối quan hệ RELATED_TO học thuật.")

if __name__ == "__main__":
    run_migration()
