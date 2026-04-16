import pandas as pd

files = [
    ("output_ngoai_van.csv", "book"),
    ("output_tieng_viet.csv", "book"),
    ("output_giao_trinh.csv", "book"),
    ("output_luan_van.csv", "thesis"),
    ("output_bai_bao.csv", "article"),
]

dfs = []

for file, doc_type in files:
    try:
        df = pd.read_csv(file)

        # thêm type
        df["type"] = doc_type

        # ❌ bỏ dòng rỗng
        df = df.dropna(how="all")

        dfs.append(df)

        print(f"✅ Loaded: {file} ({len(df)} rows)")

    except Exception as e:
        print(f"❌ Lỗi file {file}: {e}")

# gộp lại
df_all = pd.concat(dfs, ignore_index=True)

# ❌ xóa trùng (rất quan trọng)
df_all = df_all.drop_duplicates(subset=["title", "publisher_info"])

# reset index
df_all = df_all.reset_index(drop=True)

# lưu file
df_all.to_csv("final_data.csv", index=False, encoding="utf-8-sig")

print("🎉 DONE → final_data.csv")
print("Tổng số dòng:", len(df_all))