import requests
import PyPDF2
import docx  # สำหรับอ่าน .docx
import os

# === อ่าน PDF ===
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text.strip()

# === อ่าน DOCX ===
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])

# === เลือกวิธีอ่านตามนามสกุล ===
def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type: only .pdf and .docx are supported.")

# === สร้าง Prompt ===
def build_prompt_from_document(doc_text, question):
    return f"""Based on the following document, answer the question below.

Document:
\"\"\"
{doc_text}
\"\"\"

Question: {question}
Answer:"""

# === ส่งคำถามไปยังโมเดล LLM ===
def ask_question_from_file(file_path, question):
    doc_text = extract_text_from_file(file_path)
    doc_text = doc_text[:500]  # จำกัดความยาวตามที่ต้องการ
    prompt = build_prompt_from_document(doc_text, question)

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'llama3.2',
            'prompt': prompt,
            'stream': False
        }
    )

    print("คำตอบจากโมเดล:", response.json()["response"])

# === ทดสอบการใช้งาน ===
file_path = "testdoc2_th.pdf"  # เปลี่ยนชื่อไฟล์เป็น .pdf หรือ .docx ได้
question = "หัวข้อหลักคืออะไร และการทำง่นทำงานยังไง?"

ask_question_from_file(file_path, question)
