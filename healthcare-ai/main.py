import os
import re
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OLLAMA_API_KEY  = os.getenv("OLLAMA_API_KEY")

llm            = None
ollama_client  = None
tool           = lambda f: f  

try:
    from langchain_mistralai import ChatMistralAI
    from langchain_core.tools import tool
    if MISTRAL_API_KEY:
        llm = ChatMistralAI(api_key=MISTRAL_API_KEY, model="mistral-small-latest")
except ImportError:
    pass

try:
    import ollama
    if OLLAMA_API_KEY:
        ollama_client = ollama.Client(headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"})
except ImportError:
    pass


@tool
def ollama_websearch(query: str):
    if not ollama_client:
        return {"results": []}
    try:
        return ollama_client.web_search(query)
    except Exception as exc:
        return {"results": [], "error": str(exc)}


def clean_content(text: str) -> str:
    if not text:
        return "No content available."

    match = re.search(r'##\s*Summary\s*\n+([\s\S]+?)(?=\n##\s|\Z)', text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    else:
        cut_pattern = (
            r'\n##\s*(You May Also Like|Related Articles?|Trending Topics?|Quick Links?|'
            r'Health Categories|Other Popular|Entities|Companies|Frequently Asked|'
            r'Better health|Related Tags|SEE ALSO|Legal)'
        )
        text = re.split(cut_pattern, text, maxsplit=1, flags=re.IGNORECASE)[0]

        boilerplate = [
            r'^Published:.*$', r'^Author:.*$', r'^Type:.*$',
            r'^Advertisement\s*$', r'^Subscribe\s*$',
            r'^.*newsletter.*$', r'^.*reCAPTCHA.*$',
            r'^.*non-profit.*$', r'^.*Advertising on our site.*$',
            r'^.*privacy policy.*$', r'^.*editorial process.*$',
            r'^Rendered:.*$', r'^Source:.*Getty.*$',
            r'^Image content:.*$', r'^View image online\s*\(.*?\)$',
            r'^https?://\S+\s*$',
        ]
        for pattern in boilerplate:
            text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)

        text = re.sub(r'\n{3,}', '\n\n', text).strip()

        if len(text) > 800:
            cut = text[:800]
            last_dot = max(cut.rfind('. '), cut.rfind('.\n'))
            text = cut[:last_dot + 1] if last_dot > 400 else cut

    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    return text or "No clear summary available."


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


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chat")
async def chat(prompt: str):
    if not ollama_client:
        return JSONResponse({"error": "OLLAMA_API_KEY not configured"}, status_code=503)

    result = ollama_websearch.invoke({"query": prompt})
    entries = result.get("results") if isinstance(result, dict) else getattr(result, "results", [])

    if not entries:
        return JSONResponse({"results": [{"response": "No results found.", "ref": None}]})

    results = []
    for item in entries:
        raw_content = item.get("content", "") if isinstance(item, dict) else getattr(item, "content", "")
        url         = item.get("url", "No reference") if isinstance(item, dict) else getattr(item, "url", "No reference")
        results.append({
            "response": clean_content(raw_content or ""),
            "ref":      url,
        })

    return JSONResponse({"results": results})