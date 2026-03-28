"""
Tammeny — General Medical Chatbot with Web Search
Run with: uvicorn main:app --reload --port 8002
"""

import os
import re
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OLLAMA_API_KEY  = os.getenv("OLLAMA_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY is missing. Check your .env file.")

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
import ollama

llm = ChatMistralAI(api_key=MISTRAL_API_KEY, model="mistral-small-latest")

client = ollama.Client(headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"}) if OLLAMA_API_KEY else None


@tool
def ollama_websearch(query: str):
    """Performs a web search using the Ollama API."""
    if not client:
        return {"results": []}
    response = client.web_search(query)
    return response


def clean_content(text):
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\n+', '\n', text).strip()
    return text


app = FastAPI(title="Tammeny Web Search Medical API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def welcome():
    return {"message": "Tammeny Web Search Medical API is running"}


@app.post("/chat")
async def chat(prompt: str):
    if not client:
        return JSONResponse({"error": "OLLAMA_API_KEY not configured"}, status_code=503)

    x = ollama_websearch.invoke(prompt)
    results = []

    if "results" in x and len(x["results"]) > 0:
        for item in x["results"]:
            results.append({
                "response": clean_content(item.content),
                "ref": item.url if hasattr(item, "url") else "No reference"
            })
    else:
        results.append({"response": "No results found.", "ref": None})

    return JSONResponse({"results": results})