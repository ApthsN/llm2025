import requests
import PyPDF2
import docx
import os
import gradio as gr

# === ฟังก์ชันอ่าน PDF ===
def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text()
    return text.strip()

# === ฟังก์ชันอ่าน DOCX ===
def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])

# === ฟังก์ชันรวมสำหรับอ่านไฟล์ทุกประเภท ===
def extract_text(file_obj):
    name = file_obj.name
    ext = os.path.splitext(name)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_obj)
    elif ext == ".docx":
        return extract_text_from_docx(file_obj)
    else:
        raise ValueError("รองรับเฉพาะไฟล์ .pdf และ .docx เท่านั้น")

# === สร้าง Prompt แบบ RAG ===
def build_prompt(doc_text, question):
    return f"""Based on the following document, answer the question below.

Document:
\"\"\"
{doc_text}
\"\"\"

Question: {question}
Answer:"""

# === ฟังก์ชันหลัก ===
def ask_from_file(file_obj, question):
    try:
        doc_text = extract_text(file_obj)
        doc_text = doc_text[:500]  # จำกัดขนาดข้อความ
        prompt = build_prompt(doc_text, question)

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': prompt,
                'stream': False
            }
        )
        data = response.json()
        return data.get("response", "⚠️ ไม่พบคำตอบจากโมเดล")

    except requests.exceptions.ConnectionError:
        return "❌ ไม่สามารถเชื่อมต่อกับ Ollama ได้ กรุณาตรวจสอบว่า Ollama ทำงานอยู่หรือไม่"
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {e}"

# === GUI ด้วย Gradio ===
with gr.Blocks(title="ผู้ช่วย AI อ่านเอกสาร") as demo:
    gr.Markdown("## 📄🧠 ผู้ช่วย AI สำหรับตอบคำถามจากไฟล์ PDF / DOCX\nอัปโหลดเอกสาร และถามคำถามเพื่อรับคำตอบจาก AI")

    with gr.Column():
        file_input = gr.File(label="📂 เลือกไฟล์ PDF หรือ DOCX", file_types=[".pdf", ".docx"])
        question_input = gr.Textbox(label="❓ ป้อนคำถามของคุณ", placeholder="เอกสารนี้พูดถึงเรื่องอะไร?", lines=2)
        submit_btn = gr.Button("ถามคำถาม")
        output_box = gr.Textbox(label="🧠 คำตอบจากโมเดล", lines=10)

    submit_btn.click(fn=ask_from_file, inputs=[file_input, question_input], outputs=output_box)

demo.launch()
