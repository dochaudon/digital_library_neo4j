import csv

INPUT_FILE = "database/dataset/node_document.csv"
OUTPUT_FILE = "database/dataset/node_document_update.csv"


def process():
    with open(INPUT_FILE, newline='', encoding="utf-8") as infile, \
         open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            doc_id = row["id"]
            doc_type = row["type"]

            # 🔥 file pdf (tất cả đều có)
            row["file_url"] = f"/static/uploads/files/{doc_id}.pdf"

            # 🔥 ảnh (article không có)
            if doc_type == "article":
                row["image_url"] = ""
            else:
                row["image_url"] = f"/static/uploads/images/{doc_id}.jpg"

            writer.writerow(row)

    print("✅ DONE → database/dataset/final_data_ready.csv")


if __name__ == "__main__":
    process()