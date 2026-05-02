import csv

INPUT_FILE = r"D:\DATN\digitallibrary\database\dataset\node_document.csv"
OUTPUT_FILE = r"D:\DATN\digitallibrary\database\dataset\data_cleaned.csv"

DEFAULT_IMAGE = "/static/uploads/images/pdf.jpg"

with open(INPUT_FILE, newline='', encoding='utf-8') as infile, \
     open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)

    writer.writeheader()

    for row in reader:
        # chỉ xử lý article
        if row.get('type') == 'article':
            row['image_url'] = DEFAULT_IMAGE

        writer.writerow(row)

print("✅ Done: chỉ update image cho article")