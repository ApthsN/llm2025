import pdfplumber
import docx
from sentence_transformers import SentenceTransformer
import faiss
from transformers import pipeline

def read_pdf_text(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
    return text

def read_docx_text(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def split_text(text, max_length=500):
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_length:
            current_chunk += para + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + " "
    chunks.append(current_chunk.strip())
    return chunks

# โหลดโมเดล
embedder = SentenceTransformer("all-MiniLM-L6-v2")
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# เลือกไฟล์
file_path = "EdgeAI_en.pdf"  # หรือ "document.docx"

if file_path.endswith(".pdf"):
    document_text = read_pdf_text(file_path)
elif file_path.endswith(".docx"):
    document_text = read_docx_text(file_path)
else:
    raise ValueError("รองรับเฉพาะ .pdf และ .docx")

chunks = split_text(document_text)
embeddings = embedder.encode(chunks)

# FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# ฟังก์ชันถามตอบ (เลือกตอบแบบสั้น/ยาวได้)
def ask_question(question, top_k=3, answer_length="short"):
    question_vec = embedder.encode([question])
    _, indices = index.search(question_vec, top_k)
    context = " ".join([chunks[i] for i in indices[0]])

    # กำหนดคำตอบแบบสั้นหรือยาว (ผ่าน context)
    if answer_length == "long":
        context += " " * 300  # trick: ขยาย context ให้โมเดลตอบยาวขึ้น

    result = qa_pipeline(question=question, context=context)
    return result['answer']

# ทดลองใช้งาน
question = "What is Edge AI"
answer = ask_question(question, top_k=3, answer_length="short")
print("คำตอบแบบสั้น:", answer)

answer_long = ask_question(question, top_k=3, answer_length="long")
print("คำตอบแบบยาว:", answer_long)
