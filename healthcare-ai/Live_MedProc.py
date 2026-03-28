import os
import base64
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

HF_ROUTER_TOKEN = os.getenv("HF_ROUTER_TOKEN")

API_URL    = "https://router.huggingface.co/v1/chat/completions"
MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct:hyperbolic"
HEADERS    = {"Authorization": f"Bearer {HF_ROUTER_TOKEN}"} if HF_ROUTER_TOKEN else {}

SYSTEM_PROMPT = """You are Tammeny (طمّني), a warm, caring, and knowledgeable health assistant.

STRICT RULES:
1. LANGUAGE DETECTION IS YOUR TOP PRIORITY.
   - If the user writes in English → reply ENTIRELY in English. Not a single Arabic word.
   - If the user writes in Arabic  → reply ENTIRELY in Arabic.  Not a single English word.
   - Detect language from the CURRENT message, not previous ones.
   - When in doubt, use English.
2. Use simple, plain language. If you use a medical term, explain it in parentheses.
3. Be warm, clear, and reassuring — never alarming or dismissive.
4. Describe what you observe in the image in plain terms.
5. NEVER provide a clinical diagnosis. Always end with a recommendation to consult a doctor.
6. Keep your response concise"""

app = FastAPI(title="Tammeny Vision API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health():
    return {"status": "running", "service": "Tammeny Vision API"}


@app.post("/analyze_image/")
async def analyze_image(
    image: UploadFile = File(...),
    human_prompt: str = Form(
        default="Please describe what you see in this medical image in simple language that a patient can understand."
    ),
):
    if not HF_ROUTER_TOKEN:
        return JSONResponse(status_code=503, content={"error": "HF_ROUTER_TOKEN is not configured"})

    try:
        img_bytes    = await image.read()
        img_b64      = base64.b64encode(img_bytes).decode()
        content_type = image.content_type or "image/jpeg"

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": human_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:{content_type};base64,{img_b64}"}},
                    ],
                },
            ],
            "max_tokens": 600,
        }

        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=45)

        if resp.status_code != 200:
            return JSONResponse(
                status_code=resp.status_code,
                content={"error": f"Vision API error: {resp.text}"},
            )

        message = resp.json()["choices"][0]["message"]
        return {"response": message.get("content", ""), "role": message.get("role", "assistant")}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})