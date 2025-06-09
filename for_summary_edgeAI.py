import pdfplumber
import docx
from transformers import pipeline

# ฟังก์ชันอ่าน PDF
def read_pdf_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

# ฟังก์ชันอ่าน DOCX
def read_docx_text(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# ฟังก์ชันแบ่งเนื้อหาเป็นย่อหน้า (chunk)
def split_text(text, max_chunk_length=1000):
    paragraphs = text.split("\n")
    chunks, current_chunk = [], ""
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chunk_length:
            current_chunk += para + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + " "
    chunks.append(current_chunk.strip())
    return chunks

# ---------- CONFIG ----------
# ตั้งค่าไฟล์
file_path = "EdgeAI_en.pdf"  # หรือ "document.docx"

# เลือกโมเดลสรุปข้อความ
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# ---------- LOAD DOCUMENT ----------
if file_path.endswith(".pdf"):
    document_text = read_pdf_text(file_path)
elif file_path.endswith(".docx"):
    document_text = read_docx_text(file_path)
else:
    raise ValueError("รองรับเฉพาะ .pdf และ .docx")

chunks = split_text(document_text)

# ---------- สรุปเนื้อหา ----------
print("📄 กำลังสรุปเนื้อหาทั้งหมด...")
final_summary = ""
for i, chunk in enumerate(chunks):
    if len(chunk.strip()) < 50:
        continue  # ข้าม chunk ที่สั้นเกินไป
    summary = summarizer(chunk, max_length=200, min_length=30, do_sample=False)[0]['summary_text']
    final_summary += f"{summary}\n\n"

# ---------- แสดงผล ----------
print("\n✅ สรุปเนื้อหาทั้งหมด:\n")
print(final_summary)

# ---------- บันทึกเป็นไฟล์ (ทางเลือก) ----------
with open("summary_output.txt", "w", encoding="utf-8") as f:
    f.write(final_summary)
