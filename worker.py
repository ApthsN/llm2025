#worker.py
from celery import Celery
import os

celery_app = Celery("tasks", broker=os.getenv("REDIS_URL", "redis://redis:6379/0"))

@celery_app.task
def dummy_task(message):
    return f"รับข้อความจากผู้ใช้: {message}"
