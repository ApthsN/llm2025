#app.py
import os
import gradio as gr
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def ask_model(prompt):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            }
        )
        data = response.json()
        return data.get("response", "⚠️ ไม่พบคำตอบจากโมเดล หรือโมเดลยังไม่ทำงาน")
    except requests.exceptions.ConnectionError:
        return "❌ ไม่สามารถเชื่อมต่อกับ Ollama ได้ กรุณาตรวจสอบว่า Ollama ทำงานอยู่หรือไม่"
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {e}"

with gr.Blocks(title="ผู้ช่วย AI ภาษาไทย (Offline)") as demo:
    gr.Markdown("## 🧠 ผู้ช่วย AI ภาษาไทย (ทำงานออฟไลน์)")
    with gr.Column():
        input_box = gr.Textbox(label="คำถาม", placeholder="ป้อนคำถาม", lines=3)
        submit_btn = gr.Button("ถาม")
        output_box = gr.Textbox(label="คำตอบ", lines=10)
    submit_btn.click(fn=ask_model, inputs=input_box, outputs=output_box)

demo.launch(server_name="0.0.0.0", server_port=7860)
