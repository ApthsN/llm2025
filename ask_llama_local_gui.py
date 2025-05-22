import gradio as gr
import requests

def ask_model(prompt):
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3.2',
                'prompt': prompt,
                'stream': False
            }
        )
        data = response.json()
        return data.get("response", "⚠️ ไม่พบคำตอบจากโมเดล หรือโมเดลยังไม่ทำงาน")
    except requests.exceptions.ConnectionError:
        return "❌ ไม่สามารถเชื่อมต่อกับ Ollama ได้ กรุณาตรวจสอบว่า Ollama ทำงานอยู่หรือไม่"
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {e}"

with gr.Blocks(title="ผู้ช่วย AI ภาษาไทย (Offline)") as demo:
    gr.Markdown("## 🧠 ผู้ช่วย AI ภาษาไทย (ทำงานออฟไลน์)\nกรุณาป้อนคำถามด้านล่าง แล้วกดปุ่มเพื่อดูคำตอบ")

    with gr.Column():
        input_box = gr.Textbox(
            label="ป้อนคำถามเป็นภาษาไทย",
            placeholder="เช่น: อธิบายหลักการทำงานของ Edge AI",
            lines=3
        )

        submit_btn = gr.Button("ถามคำถาม")

        output_box = gr.Textbox(
            label="คำตอบจากโมเดล",
            lines=10
        )

    submit_btn.click(fn=ask_model, inputs=input_box, outputs=output_box)

demo.launch()
