import fitz  # PyMuPDF
import re
import json
import os

def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        all_text += s["text"] + "\n"
    return all_text.strip()

def extract_fields(text):
    fields = {}

    # Extract invoice number
    inv_match = re.search(r"Text1:\s*(\S+)", text)
    if inv_match:
        fields["Invoice_Number"] = inv_match.group(1).strip()

    # Extract date
    date_match = re.search(r"Text2:\s*(.+)", text)
    if date_match:
        fields["Date"] = date_match.group(1).strip()

    # Extract email
    email_match = re.search(r"Text9:\s*(\S+@\S+)", text)
    if email_match:
        fields["Email"] = email_match.group(1).strip()

    # Extract phone
    phone_match = re.search(r"Text10:\s*(\(?\d+\)?[\s\-]?\d+[\s\-]?\d+)", text)
    if phone_match:
        fields["Phone"] = phone_match.group(1).strip()

    # Extract total
    total_match = re.search(r"Text83:\s*([\d,.]+)", text)
    if total_match:
        fields["Total"] = total_match.group(1).strip()

    return fields

def extract_products(text):
    lines = text.split("\n")
    items = []
    temp = []
    pattern = re.compile(r'^\d+$')  # to detect numeric codes

    for i in range(len(lines)):
        if "overcoat" in lines[i] or "perfume" in lines[i] or "blazer" in lines[i] or "dress" in lines[i]:
            temp = [lines[i]]
            for j in range(1, 7):
                if i + j < len(lines):
                    temp.append(lines[i + j])
            if len(temp) >= 7:
                items.append({
                    "PRODUCT NAME": temp[0],
                    "ITEM #": temp[1],
                    "PRICE": temp[2],
                    "QTY": temp[3],
                    "SIZE": temp[4],
                    "COLOUR": temp[5],
                    "TOTAL": temp[6]
                })

    return items

def process_invoice(pdf_path):
    text = extract_text_blocks(pdf_path)
    fields = extract_fields(text)
    items = extract_products(text)

    result = {
        "File": os.path.basename(pdf_path),
        "Extracted_Fields": fields,
        "Items_Table": items,
        "Raw_Text_Preview": text[:300]
    }

    output_path = os.path.splitext(os.path.basename(pdf_path))[0] + "_output.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"✅ Output saved to: {output_path}")

# === RUN ===
if __name__ == "__main__":
    process_invoice("Document Extraction 2.pdf")
