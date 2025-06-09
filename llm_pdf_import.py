import requests
import PyPDF2

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text.strip()

def build_prompt_from_document(doc_text, question):
    return f"""Based on the following document, answer the question below.

Document:
\"\"\"
{doc_text}
\"\"\"

Question: {question}
Answer:"""

def ask_question_from_pdf(pdf_path, question):
    doc_text = extract_text_from_pdf(pdf_path)
    doc_text = doc_text[:500]
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

# ===== แก้ตรงนี้เพื่อทดลอง =====
pdf_path = "testdoc1_en.pdf"  # เปลี่ยนชื่อไฟล์ถ้าจำเป็น
question = "What is the main idea of the document?"

ask_question_from_pdf(pdf_path, question)
