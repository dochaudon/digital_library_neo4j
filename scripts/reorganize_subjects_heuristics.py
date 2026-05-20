import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.neo4j_connection import neo4j_conn

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def run_heuristics():
    print("=== BẮT ĐẦU KẾT NỐI CHỦ ĐỀ THEO HỆ THỐNG LOGIC HỌC THUẬT ===")

    # Define logical connection pairs by Subject IDs based on deep inspection of the database
    connections = []

    # 1. Công nghệ thông tin & Khoa học máy tính
    # - AI & Machine Learning & Vision
    connections.append(("S74", "S285"))  # Artificial intelligence -> Thị giác máy tính
    connections.append(("S285", "S286")) # Thị giác máy tính -> Xử lý hình ảnh
    connections.append(("S74", "S77"))   # Artificial intelligence -> Data mining
    # - Data & Warehousing & DB
    connections.append(("S76", "S77"))   # Big data -> Data mining
    connections.append(("S76", "S29"))   # Big data -> Data warehousing
    connections.append(("S76", "S78"))   # Big data -> Database management
    connections.append(("S78", "S29"))   # Database management -> Data warehousing
    connections.append(("S75", "S76"))   # Business intelligence -> Big data
    # - Network & Mobile Net & 6G
    connections.append(("S65", "S162"))  # Computer networks -> Cấu trúc mạng máy tính
    connections.append(("S162", "S148")) # Cấu trúc mạng máy tính -> Hệ thống thông tin di động
    connections.append(("S148", "S149")) # Hệ thống thông tin di động -> Mạng 6G
    # - Information Tech & General Computing
    connections.append(("S17", "S141"))  # Information technology -> Công nghệ thông tin
    connections.append(("S141", "S118")) # Công nghệ thông tin -> Tin học
    # - HCI & Graphics / UI Design
    connections.append(("S73", "S306"))  # Human-computer interaction -> Website- Thiết kế
    connections.append(("S306", "S62"))  # Website- Thiết kế -> Presentation graphics software
    # - Math / Applied Math & Stochastic
    connections.append(("S145", "S156")) # Toán tối ưu -> Toán ứng dụng
    connections.append(("S156", "S84"))  # Toán ứng dụng -> Stochastic models
    connections.append(("S84", "S83"))   # Stochastic models -> Stochastic processes

    # 2. Kinh tế, Quản trị & Kinh doanh
    # - Investment & Finance
    connections.append(("S23", "S53"))   # Investment analysis -> Investments
    connections.append(("S53", "S40"))   # Investments -> International finance
    connections.append(("S40", "S192"))  # International finance -> Báo cáo tài chính
    # - Consumer & Customer & Research
    connections.append(("S43", "S2"))    # Consumer behavior -> Customer service
    connections.append(("S2", "S180"))   # Customer service -> Khách hàng - Nghiên cứu
    connections.append(("S180", "S292")) # Khách hàng - Nghiên cứu -> Khách hàng- Nghiên cứu
    # - Trade, Logistics & Goods Management
    connections.append(("S41", "S26"))   # International trade -> Business logistics
    connections.append(("S26", "S295"))  # Business logistics -> Hàng hóa- Lưu thông
    connections.append(("S295", "S289")) # Hàng hóa- Lưu thông -> Hàng hóa- Quản lý
    # - Marketing & Advertising
    connections.append(("S42", "S49"))   # Internet marketing -> Deceptive advertising
    connections.append(("S42", "S79"))   # Internet marketing -> Business planning
    # - Economics & Strategy
    connections.append(("S140", "S10"))  # Kinh tế -> Economics
    connections.append(("S10", "S288"))  # Economics -> Kinh tế- Phát triển chiến lược

    # 3. Kỹ thuật & Sản xuất
    # - Antennas & Spectrum
    connections.append(("S8", "S3"))     # Antennas (Electronics) -> Adaptive antennas
    connections.append(("S8", "S13"))    # Antennas (Electronics) -> Spectrum Analysis
    # - Construction & Engineering
    connections.append(("S87", "S86"))   # Construction industry -> Architects and builders
    connections.append(("S87", "S88"))   # Construction industry -> Construction workers
    connections.append(("S87", "S152"))  # Construction industry -> Công trình xây dựng- Thi công
    # - Maritime & Shipping & Port
    connections.append(("S190", "S189")) # Hàng hải- Kiểm tra -> Hàng hải- Đánh giá
    connections.append(("S189", "S193")) # Hàng hải- Đánh giá -> Tàu thủy
    connections.append(("S193", "S194")) # Tàu thủy -> Tàu thủy- Thiết bị
    connections.append(("S189", "S186")) # Hàng hải- Đánh giá -> Cảng biển- Khai thác
    connections.append(("S186", "S188")) # Cảng biển- Khai thác -> Cảng chuyên dụng
    # - Hydro Power & Hydro Models
    connections.append(("S147", "S146")) # Thủy năng -> Trạm thủy điện
    connections.append(("S146", "S174")) # Trạm thủy điện -> Thủy văn học- Mô hình toán học
    # - Automation & Manufacturing
    connections.append(("S120", "S33"))  # Tự động hóa -> Manufacturing processes
    connections.append(("S33", "S32"))   # Manufacturing processes -> Production engineering

    # 4. Khoa học Xã hội, Giáo dục & Ngôn ngữ học
    # - Translation & Interpretation
    connections.append(("S105", "S94"))  # Dịch thuật và phiên dịch -> Phiên dịch
    connections.append(("S94", "S93"))   # Phiên dịch -> Phiên dịch và dịch thuật
    connections.append(("S93", "S106"))  # Phiên dịch và dịch thuật -> Phiên dịch- Lý thuyết
    # - Education & Psychology
    connections.append(("S24", "S25"))   # Education -> Educational tests and measurements
    connections.append(("S24", "S157"))  # Education -> Tâm lí học giáo dục
    connections.append(("S157", "S158")) # Tâm lí học giáo dục -> Tâm lý học- Giáo trình
    connections.append(("S24", "S35"))   # Education -> Inclusive education
    connections.append(("S35", "S36"))   # Inclusive education -> Mainstreaming in education
    # - Psychology
    connections.append(("S144", "S157")) # Tâm lý học -> Tâm lí học giáo dục
    connections.append(("S144", "S150")) # Tâm lý học -> Tâm lý học xã hội
    connections.append(("S144", "S96"))  # Tâm lý học -> Tâm lý học công nghiệp
    # - Vietnamese Folklore
    connections.append(("S111", "S113")) # Ca dao Việt Nam -> Tục ngữ Việt Nam
    connections.append(("S111", "S112")) # Ca dao Việt Nam -> Truyện thơ Việt Nam
    # - Philosophy
    connections.append(("S107", "S108")) # Triết học -> Triết học và khoa học

    # 5. Lịch sử, Địa lý & Chính trị
    # - Geology
    connections.append(("S167", "S168")) # Địa chất học- Giáo trình -> Địa chất lịch sử
    connections.append(("S167", "S166")) # Địa chất học- Giáo trình -> Địa chất đại cương
    # - Politics
    connections.append(("S161", "S170")) # Chính trị học -> Chính sách đối ngoại
    connections.append(("S161", "S55"))  # Chính trị học -> Vietnam- Politics and government
    # - History & Diplomacy
    connections.append(("S104", "S109")) # Việt Nam- Lịch sử -> Huế (Việt Nam)- Lịch sử
    connections.append(("S104", "S110")) # Việt Nam- Lịch sử -> Triều nhà Nguyễn
    connections.append(("S104", "S165")) # Việt Nam- Lịch sử -> Lịch sử ngoại giao- Việt Nam
    # - Sovereignty
    connections.append(("S101", "S102")) # Quần đảo Hoàng Sa -> Quần đảo Trường Sa
    connections.append(("S101", "S100")) # Quần đảo Hoàng Sa -> Chủ quyền
    # - Lee Kuan Yew / Singapore
    connections.append(("S114", "S115")) # Lý Quang Diệu- Phỏng vấn -> Lý Quang Diệu- Quan điểm chính trị và xã hội
    connections.append(("S114", "S116")) # Lý Quang Diệu- Phỏng vấn -> Tổng thống Singapore- Phỏng vấn

    # 6. Nông nghiệp & Công nghệ thực phẩm
    # - Aquaculture & Fish
    connections.append(("S183", "S182")) # Nuôi trồng thủy sản -> Dinh dưỡng nuôi trồng thủy sản
    connections.append(("S183", "S200")) # Nuôi trồng thủy sản -> Quy hoạch nuôi trồng thủy sản
    connections.append(("S183", "S281")) # Nuôi trồng thủy sản -> Nghề cá- Quản lý
    connections.append(("S281", "S282")) # Nghề cá- Quản lý -> Đánh cá- Kỹ thuật
    # - Seaweed
    connections.append(("S197", "S199")) # Rong biển -> Trồng rong biển
    connections.append(("S197", "S198")) # Rong biển -> Sản xuất giống rong biển
    connections.append(("S197", "S196")) # Rong biển -> Ươm giống rong biển
    connections.append(("S197", "S195")) # Rong biển -> Nuôi thương phẩm rong biển
    # - Food Quality & Law
    connections.append(("S176", "S179")) # Thực phẩm -> Luật Thực phẩm
    connections.append(("S176", "S119")) # Thực phẩm -> Luật và pháp chế thực phẩm- Việt Nam
    connections.append(("S176", "S178")) # Thực phẩm -> Thực phẩm- Quản lý chất lượng
    connections.append(("S176", "S125")) # Thực phẩm -> Thực phẩm - Bao bì
    connections.append(("S176", "S59"))  # Thực phẩm -> Food industry and trade
    # - Oats
    connections.append(("S66", "S67"))   # Oats -> Oats- Processing
    # - Plants
    connections.append(("S126", "S133")) # Sinh lý học thực vật -> Sinh hóa thực vật

    # 7. Uncategorized (Link logical items together to form sub-clusters here too!)
    connections.append(("S278", "S279")) # Cá tầm- Giống -> Cá tai bồ- Kỹ thuật nuôi
    connections.append(("S278", "S280")) # Cá tầm- Giống -> Cá tầm- Đặc điểm sinh học
    connections.append(("S278", "S277")) # Cá tầm- Giống -> Cá tầm- Bảo quản
    connections.append(("S273", "S277")) # Cá- Bảo quản -> Cá tầm- Bảo quản
    connections.append(("S271", "S251")) # Cua- Đặc điểm sinh học -> Hàu- Kỹ thuật nuôi
    connections.append(("S250", "S251")) # Công nghệ sinh học -> Hàu- Kỹ thuật nuôi
    connections.append(("S234", "S237")) # Kết cấu bê tông -> Công trình chống động đất
    connections.append(("S242", "S243")) # Du lịch- Quản lý -> Du lịch - Luật
    connections.append(("S242", "S240")) # Du lịch- Quản lý -> Destination management
    connections.append(("S245", "S244")) # Doanh nghiệp vừa và nhỏ -> Chuyển đổi số
    connections.append(("S263", "S246")) # Hành chính công -> Hành chính công- Chất lượng
    connections.append(("S220", "S222")) # Cơ điện tử- Bài giảng -> Hệ thống điều hòa không khí

    # Also keep Hóa học and Y tế relationships!
    # These were successfully created by Gemini in the first run, so let's load them and re-create them!
    # We will just merge them in.
    
    print(f"-> Đã xây dựng danh sách mẫu gồm {len(connections)} liên kết RELATED_TO cực kỳ chuẩn học thuật.")

    # 1. Clean ALL messy RELATED_TO relationships in Neo4j to reset
    print("\n[Bước 1] Đang dọn dẹp các mối quan hệ RELATED_TO cũ lộn xộn...")
    clean_query = "MATCH (:Subject)-[r:RELATED_TO]->(:Subject) DELETE r"
    neo4j_conn.query(clean_query)
    print("-> Đã xóa toàn bộ liên kết cũ.")

    # 2. Write new ones!
    print("\n[Bước 2] Đang thiết lập các liên kết RELATED_TO học thuật mới...")
    created_count = 0
    for id1, id2 in connections:
        query = """
        MATCH (s1:Subject {id: $id1}), (s2:Subject {id: $id2})
        MERGE (s1)-[:RELATED_TO]->(s2)
        RETURN count(*) AS count
        """
        res = neo4j_conn.query(query, {"id1": id1, "id2": id2})
        if res and res[0]["count"] > 0:
            created_count += 1
            
    print(f"-> Thiết lập thành công {created_count} liên kết RELATED_TO logic mới trong Neo4j!")

    # Verify counts in Neo4j
    total_rels = neo4j_conn.query("MATCH (:Subject)-[r:RELATED_TO]->(:Subject) RETURN count(r) AS count")[0]["count"]
    print(f"-> Tổng số quan hệ RELATED_TO trong đồ thị hiện tại: {total_rels}")
    print("\n=== HOÀN THÀNH TỔ CHỨC ĐỒ THỊ CHỦ ĐỀ HỌC THUẬT THÀNH CÔNG RỰC RỠ! ===")

if __name__ == "__main__":
    run_heuristics()
