"""
Tammeny — RAG Chatbot with Memory & General Fallback
Run with: python rag_chatbot.py
Serves on http://localhost:8000
"""

import os
import uvicorn
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY       = os.getenv("MISTRAL_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY missing — check your .env file.")
if not HUGGINGFACE_API_TOKEN:
    raise ValueError("HUGGINGFACEHUB_API_TOKEN missing — check your .env file.")

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACE_API_TOKEN

from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(title="Tammeny Health Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── LLM & Embeddings ──────────────────────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)

llm = ChatMistralAI(api_key=MISTRAL_API_KEY, model="mistral-small-latest")

# ── In-memory stores ──────────────────────────────────────────────────────────
session_store: Dict[str, BaseChatMessageHistory] = {}
vectorstore_cache: Dict[str, FAISS] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]


# ── System prompt (shared) ────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are Tammeny (طمّني), a warm, caring, and knowledgeable health assistant.

STRICT RULES:
1. Detect the language of the user's message and ALWAYS reply in the EXACT SAME language (Arabic or English). Never mix.
2. Use simple, plain language anyone can understand. If you must use a medical term, explain it immediately in parentheses.
3. Keep answers clear, concise, and reassuring — never cold or clinical.
4. NEVER diagnose a patient or prescribe medication. Always recommend consulting a doctor for serious concerns.
5. If the uploaded document contains relevant information, use it. Otherwise use general medical knowledge.
6. End every response with a warm follow-up question such as: "هل تريد أن أشرح أكثر؟" (Arabic) or "Would you like me to explain more?" (English).

{context}"""

CONTEXTUALIZE_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "Given the chat history and the latest user question, rewrite it as a clear standalone question. "
     "Keep the same language as the user (Arabic or English). Do NOT answer — only rewrite."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/")
async def serve_html():
    return FileResponse("chatbot_ui.html")


@app.post("/load_pdf/")
async def load_pdf(file: UploadFile = File(...), session_id: str = Form(...)):
    os.makedirs("temp_uploads", exist_ok=True)
    os.makedirs("vectors", exist_ok=True)

    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Only PDF files are supported."})

    file_path = f"temp_uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = splitter.split_documents(docs)

        vs = FAISS.from_documents(splits, embeddings)
        vs_path = f"vectors/{session_id}"
        os.makedirs(vs_path, exist_ok=True)
        vs.save_local(vs_path)
        vectorstore_cache[session_id] = vs

        return {"message": "تم رفع الملف بنجاح! يمكنك الآن السؤال عنه. | File uploaded successfully! You can now ask questions about it."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


class ChatRequest(BaseModel):
    prompt: str
    session_id: str


@app.post("/chat")
async def chat(request: ChatRequest):
    prompt    = request.prompt
    sid       = request.session_id
    vs_path   = f"vectors/{sid}"

    # ── Try to load vectorstore ───────────────────────────────────────────────
    if sid not in vectorstore_cache and os.path.exists(vs_path):
        try:
            vectorstore_cache[sid] = FAISS.load_local(
                vs_path, embeddings, allow_dangerous_deserialization=True
            )
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": str(e)})

    # ── RAG path (PDF loaded) ─────────────────────────────────────────────────
    if sid in vectorstore_cache:
        retriever = vectorstore_cache[sid].as_retriever(search_kwargs={"k": 4})

        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])

        doc_chain  = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain  = create_retrieval_chain(
            create_history_aware_retriever(llm, retriever, CONTEXTUALIZE_PROMPT),
            doc_chain,
        )

        chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )

        response = chain.invoke(
            {"input": prompt},
            config={"configurable": {"session_id": sid}},
        )
        return {"answer": response["answer"]}

    # ── General path (no PDF) ────────────────────────────────────────────────
    general_prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT.replace("{context}", "")),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    chain = RunnableWithMessageHistory(
        general_prompt | llm,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    response = chain.invoke(
        {"input": prompt},
        config={"configurable": {"session_id": sid}},
    )
    return {"answer": response.content}


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    print(f"\n🩺 Tammeny chatbot running → http://{host}:{port}\n")
    uvicorn.run(app, host=host, port=port)
