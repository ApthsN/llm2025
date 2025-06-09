# worker.py
from celery import Celery
import requests
import os

celery_app = Celery("tasks", broker=os.getenv("REDIS_URL", "redis://redis:6379/0"))

@celery_app.task
def ask_model_task(prompt):
    try:
        response = requests.post(
            f"{os.getenv('OLLAMA_URL', 'http://localhost:11434')}/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False}
        )
        data = response.json()
        return data.get("response", "⚠️ ไม่พบคำตอบ")
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {e}"
