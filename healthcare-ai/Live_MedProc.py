"""
Tammeny — Live Medical Image Analyzer (Vision AI)
Accepts an image + optional question, returns plain-language AI analysis.
Run with: uvicorn Live_MedProc:app --reload --host 127.0.0.1 --port 8001
"""

import os
import base64
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

HF_ROUTER_TOKEN = os.getenv("HF_ROUTER_TOKEN")
if not HF_ROUTER_TOKEN:
    raise ValueError("HF_ROUTER_TOKEN missing — check your .env file.")

API_URL    = "https://router.huggingface.co/v1/chat/completions"
HEADERS    = {"Authorization": f"Bearer {HF_ROUTER_TOKEN}"}
MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct:hyperbolic"

SYSTEM_PROMPT = """You are Tammeny (طمّني), a compassionate medical AI assistant.

Your job is to help patients understand their medical images in simple, clear language.

RULES:
- Detect the language of the user's question and ALWAYS reply in the SAME language (Arabic or English).
- Use plain, easy-to-understand language. Avoid complex medical jargon; if you must use a term, explain it.
- Be warm, clear, and reassuring — never alarming or dismissive.
- Describe what you observe in the image in simple terms.
- NEVER provide a clinical diagnosis. Always end with a recommendation to consult a doctor.
- Keep your response concise: 3–5 short paragraphs maximum."""

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
    try:
        img_bytes = await image.read()
        img_b64   = base64.b64encode(img_bytes).decode()

        # Detect image type
        content_type = image.content_type or "image/jpeg"

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": human_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{content_type};base64,{img_b64}"},
                        },
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

        result  = resp.json()
        message = result["choices"][0]["message"]
        return {"response": message.get("content", ""), "role": message.get("role", "assistant")}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
