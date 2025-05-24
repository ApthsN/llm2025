#app.py
import os
import gradio as gr
import time
from worker import ask_model_task

def ask_model(prompt):
    task = ask_model_task.delay(prompt)
    while not task.ready():
        time.sleep(0.5)
    return task.result

with gr.Blocks(title="ผู้ช่วย AI ภาษาไทย (Offline)") as demo:
    gr.Markdown("## 🧠 ผู้ช่วย AI ภาษาไทย (ทำงานออฟไลน์)")
    with gr.Column():
        input_box = gr.Textbox(label="คำถาม", placeholder="ป้อนคำถาม", lines=3)
        submit_btn = gr.Button("ถาม")
        output_box = gr.Textbox(label="คำตอบ", lines=10)
    submit_btn.click(fn=ask_model, inputs=input_box, outputs=output_box)

demo.launch(server_name="0.0.0.0", server_port=7860)

