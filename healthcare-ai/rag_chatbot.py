# rag_chatbot.py
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict
import os
import uvicorn

# LangChain imports
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI

# -------------------- FastAPI App Setup --------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve HTML
app.mount("/static", StaticFiles(directory="."), name="static")

# -------------------- Global LLM & Embedding Setup --------------------
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

llm = ChatMistralAI(
    api_key="QFc8aszmuCqLKlegGbh6TfxV7k6BwoCc",
    model="mistral-small-latest"
)

# -------------------- In-Memory Stores --------------------
session_store: Dict[str, BaseChatMessageHistory] = {}
vectorstore_cache: Dict[str, FAISS] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = ChatMessageHistory()
    return session_store[session_id]

# -------------------- Serve Frontend --------------------
@app.get("/")
async def serve_html():
    return FileResponse("chatbot_ui.html")

# -------------------- Upload & Process PDF --------------------
@app.post("/load_pdf/")
async def load_pdf_upload(file: UploadFile = File(...), session_id: str = Form(...)):
    os.makedirs("temp_uploads", exist_ok=True)
    os.makedirs("vectors", exist_ok=True)

    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse(status_code=400, content={"error": "Only PDF files are allowed."})

    file_location = f"temp_uploads/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        loader = PyPDFLoader(file_location)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(splits, embeddings)
        vectorstore_path = f"vectors/{session_id}"
        os.makedirs(vectorstore_path, exist_ok=True)
        vectorstore.save_local(vectorstore_path)
        vectorstore_cache[session_id] = vectorstore

        return {"message": "Uploaded successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# -------------------- Chat Endpoint --------------------
class ChatRequest(BaseModel):
    prompt: str
    session_id: str

@app.post("/chat")
async def chat_with_pdf(request: ChatRequest):
    prompt = request.prompt
    session_id = request.session_id
    vectorstore_path = f"vectors/{session_id}"

    if session_id not in vectorstore_cache:
        if os.path.exists(vectorstore_path):
            try:
                vectorstore = FAISS.load_local(
                    vectorstore_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                vectorstore_cache[session_id] = vectorstore
            except Exception as e:
                return JSONResponse(status_code=500, content={"error": str(e)})
        else:
            return JSONResponse(status_code=400, content={"error": "Please load a PDF first for this session."})

    retriever = vectorstore_cache[session_id].as_retriever()

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given a chat history and the latest user question which might reference context, formulate a standalone question."),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a medical assistant. Use the context below to answer the patient's questions accurately and concisely. Provide evidence-based information only. If unsure, respond: 'I do not have enough information to answer this.'\n\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    document_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, document_chain)

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        lambda sid: get_session_history(sid),
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    response = conversational_rag_chain.invoke(
        {"input": prompt},
        config={"configurable": {"session_id": session_id}},
    )

    return {"answer": response["answer"]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)