import re
from models.user_model import find_user_by_email, create_user, change_password
from services.auth_utils import hash_password
from database.neo4j_connection import neo4j_conn


# =========================
# FIX MISSING METADATA IDS
# =========================
def fix_missing_metadata_ids():
    labels_prefixes = {
        "Author": "A",
        "Subject": "S",
        "Keyword": "K",
        "Category": "C",
        "Language": "L",
        "Journal": "J",
        "Publisher": "P",
        "University": "U"
    }
    
    print("[MIGRATION] Checking for metadata nodes missing ID...")
    for label, prefix in labels_prefixes.items():
        # Lấy tất cả node của label này
        query_all = f"MATCH (n:{label}) RETURN n.id AS id, n.name AS name"
        results = neo4j_conn.query(query_all)
        
        missing_nodes = []
        max_num = 0
        pattern = re.compile(f"^{prefix}(\\d+)$")
        
        for res in results:
            nid = res.get("id")
            name = res.get("name")
            if not nid:
                if name:
                    missing_nodes.append(name)
            else:
                match = pattern.match(str(nid))
                if match:
                    num = int(match.group(1))
                    if num > max_num:
                        max_num = num
                        
        if missing_nodes:
            print(f"[MIGRATION] Fixing {len(missing_nodes)} {label} nodes missing ID...")
            for name in missing_nodes:
                max_num += 1
                new_id = f"{prefix}{max_num}"
                query_update = f"MATCH (n:{label} {{name: $name}}) WHERE n.id IS NULL SET n.id = $id"
                neo4j_conn.query(query_update, {"name": name, "id": new_id})
                print(f"[MIGRATION] Assigned ID {new_id} to {label} '{name}'")
            print(f"[MIGRATION] Finished fixing {label} nodes.")


# =========================
# INIT ADMIN ACCOUNT
# =========================
def init_admin_account():
    # Sửa các node metadata thiếu ID trước
    try:
        fix_missing_metadata_ids()
    except Exception as e:
        print("[MIGRATION] Error fixing missing IDs:", e)

    admin_email = "admin@gmail.com"
    admin_pass = "123456"

    # 🔍 check tồn tại
    existing_admin = find_user_by_email(admin_email)

    if existing_admin:
        print("[ADMIN] Admin already exists")
        
        # 🔥 Kiểm tra nếu hash cũ (không phải bcrypt) thì update
        current_hash = existing_admin.get("password", "")
        if not current_hash.startswith("$2b$"):
            print("[ADMIN] Legacy password hash detected. Upgrading to bcrypt...")
            new_hash = hash_password(admin_pass)
            change_password(existing_admin["id"], new_hash)
            print("[ADMIN] Admin password upgraded successfully")
        return

    # 🔥 tạo admin
    print("[ADMIN] Creating new admin account...")
    admin_data = {
        "username": "admin",
        "email": admin_email,
        "password": hash_password(admin_pass),
        "role": "admin"
    }
    
    create_user(admin_data)
    print("[ADMIN] Admin created successfully")

    print("🔥 Admin account created:")
    print("   Email: admin@gmail.com")
    print("   Password: 123456")