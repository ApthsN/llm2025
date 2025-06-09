import requests
import PyPDF2
import docx
import os
import time
import gradio as gr

# === อ่าน PDF ===
def extract_text_from_pdf(file):
    text = ""
    reader = PyPDF2.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text()
    return text.strip()

# === อ่าน DOCX ===
def extract_text_from_docx(file):
    doc = docx.Document(file)
    return '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])

# === อ่านไฟล์ทุกประเภท ===
def extract_text(file_obj):
    name = file_obj.name
    ext = os.path.splitext(name)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_obj)
    elif ext == ".docx":
        return extract_text_from_docx(file_obj)
    else:
        return ""  # ข้ามไฟล์ที่ไม่รองรับ

# === รวมข้อความจากหลายไฟล์ ===
def extract_texts_from_files(file_objs):
    all_texts = []
    for file in file_objs:
        try:
            text = extract_text(file)
            if text:
                all_texts.append(text)
        except Exception as e:
            all_texts.append(f"[ไม่สามารถอ่านไฟล์ {file.name} ได้: {e}]")
    return "\n\n".join(all_texts)

# === สร้าง prompt ===
def build_prompt(doc_text, question):
    return f"""Based on the following documents, answer the question below.

Documents:
\"\"\"
{doc_text}
\"\"\"

Question: {question}
Answer:"""

# === ฟังก์ชันหลักพร้อมจับเวลา ===
def ask_from_files(files, question):
    start_time = time.time()

    try:
        combined_text = extract_texts_from_files(files)
        combined_text = combined_text[:2000]  # ป้องกันความยาวเกิน
        prompt = build_prompt(combined_text, question)

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': prompt,
                'stream': False
            }
        )
        data = response.json()
        answer = data.get("response", "⚠️ ไม่พบคำตอบจากโมเดล")

    except requests.exceptions.ConnectionError:
        return "❌ ไม่สามารถเชื่อมต่อกับ Ollama ได้ กรุณาตรวจสอบว่า Ollama ทำงานอยู่หรือไม่"
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {e}"

    end_time = time.time()
    elapsed = end_time - start_time
    return f"{answer}\n\n🕒 ใช้เวลา {elapsed:.2f} วินาที"

# === GUI ===
with gr.Blocks(title="AI อ่านเอกสารหลายไฟล์") as demo:
    gr.Markdown("## 📚🧠 ผู้ช่วย AI อ่านหลายเอกสาร (.pdf / .docx)\nอัปโหลดไฟล์หลายรายการ แล้วถามคำถาม")

    with gr.Column():
        file_inputs = gr.File(label="📂 เลือกไฟล์หลายรายการ", file_types=[".pdf", ".docx"], file_count="multiple")
        question_input = gr.Textbox(label="❓ ป้อนคำถาม", placeholder="เอกสารทั้งหมดกล่าวถึงเรื่องอะไร?", lines=2)
        submit_btn = gr.Button("ถามคำถาม")
        output_box = gr.Textbox(label="🧠 คำตอบจากโมเดล", lines=12)

    submit_btn.click(fn=ask_from_files, inputs=[file_inputs, question_input], outputs=output_box)

demo.launch()
