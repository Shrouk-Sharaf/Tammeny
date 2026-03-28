<div align="center">

<img src="https://img.shields.io/badge/Tammeny-طمّني-2dd4bf?style=for-the-badge&labelColor=060b16" alt="Tammeny"/>

# 🩺 Tammeny — طمّني

### AI-Powered Healthcare Communication

**Bilingual health assistant for Arabic & English speakers.**  
Ask questions, upload medical files, analyze X-rays, and search medical sources — all in plain language.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Mistral](https://img.shields.io/badge/Mistral_AI-Chat_Model-ff7000?style=flat-square)](https://mistral.ai)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Qwen_2.5_VL-ffd21e?style=flat-square&logo=huggingface&logoColor=black)](https://huggingface.co)

</div>

---

## Screenshots

### 💬 Bilingual Chat

> Ask any health question in English or Arabic. Tammeny responds in your language with warm, clear advice — and always reminds you to see a doctor.

![Chat in English](D:\Tammeny\healthcare-ai\docs\screenshots\chat_eng.png)

---

### 🩻 Chest X-Ray Analysis — HIGH Severity

> Upload a chest X-ray and get instant AI screening for 14 thoracic conditions. Each finding includes a confidence score and a plain-language explanation of what it means.

![X-Ray Analysis HIGH](D:\Tammeny\healthcare-ai\docs\screenshots\xray_high.png)

---

### 🩻 Chest X-Ray Analysis — LOW Severity

> When findings are minor, Tammeny clearly reassures the patient — no panic, just the right next step.

![X-Ray Analysis LOW](D:\Tammeny\healthcare-ai\docs\screenshots\xray_low.png)

---

## 🎬 Demo Video

> Click the thumbnail below to watch the full demo.

<!-- After recording with Notch, upload to YouTube and replace YOUR_VIDEO_ID -->
[![Tammeny Demo Video](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

> 📌 **Can't see the video?** [Watch it here →](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

---

## ✨ Features

| Feature | Model | Description |
|---|---|---|
| 💬 **Bilingual Chat** | Mistral (small-latest) | Health Q&A in Arabic & English with conversation memory |
| 📄 **PDF Document Q&A** | Mistral + FAISS | Upload a medical PDF and ask questions about it |
| 🔬 **Medical Image Analysis** | Qwen2.5-VL-7B | Plain-language explanation of any medical image |
| 🩻 **Chest X-Ray Analysis** | DenseNet-121 (NIH) | Screens for 14 thoracic conditions with confidence scores |
| 🔎 **Medical Web Search** | Ollama web search | Live medical search with clean, sourced summaries |
| 🌐 **Full RTL/LTR UI** | — | Complete Arabic ↔ English toggle with layout direction switch |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  chatbot_ui.html                 │
│           (Single-page bilingual UI)             │
└────────┬──────────┬──────────┬──────────────────┘
         │          │          │          │
    Port 8000  Port 8001  Port 8002  Port 8003
         │          │          │          │
┌────────▼──┐ ┌─────▼──────┐ ┌▼──────────┐ ┌─────▼──────┐
│rag_chatbot│ │Live_MedProc│ │  server.py │ │  main.py   │
│    .py    │ │    .py     │ │ (imaging)  │ │(web search)│
│           │ │            │ │            │ │            │
│ Mistral   │ │ Qwen2.5-VL │ │DenseNet-121│ │   Ollama   │
│ + FAISS   │ │   (HF)     │ │   (NIH)    │ │ web search │
└───────────┘ └────────────┘ └────────────┘ └────────────┘
```

---

## Setup

### 1. Clone & Configure

```bash
git clone https://github.com/Shrouk-Sharaf/Tammeny
cd Tammeny
cp .env.example .env
# Edit .env and add your API keys
```

### 2. Install Dependencies

```bash
# Root (chatbot + vision)
pip install fastapi uvicorn python-multipart langchain langchain-community \
    langchain-text-splitters langchain-huggingface langchain-mistralai \
    faiss-cpu sentence-transformers pypdf python-dotenv requests

# Imaging service
cd imaging-service && pip install -r requirements.txt && cd ..
```

### 3. API Keys

| Key | Where to Get | Cost |
|---|---|---|
| `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai/) | Free tier |
| `HUGGINGFACEHUB_API_TOKEN` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | Free |
| `HF_ROUTER_TOKEN` | Same HuggingFace token | Free |

---

## ▶️ Running

Open **4 terminals**:

```bash
# Terminal 1 — Chatbot + PDF Q&A
python rag_chatbot.py
# → http://127.0.0.1:8000

# Terminal 2 — Medical Image Analysis
uvicorn Live_MedProc:app --reload --host 127.0.0.1 --port 8001
# → http://127.0.0.1:8001

# Terminal 3 — Chest X-Ray Analysis
cd imaging-service && python server.py
# → http://0.0.0.0:8002

# Terminal 4 (optional) — Web Search
python main.py
# → http://0.0.0.0:8003
```

Then open `chatbot_ui.html` in your browser.

---

## Docker (Imaging Service)

```bash
cd imaging-service
docker build -t tammeny-imaging .
docker run -p 8002:8002 tammeny-imaging
```

---

## API Reference

### Chatbot — `:8000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serve chatbot HTML UI |
| `POST` | `/load_pdf/` | Upload PDF for RAG context |
| `POST` | `/chat` | Send message `{prompt, session_id}` |

### Vision AI — `:8001`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/analyze_image/` | Analyze image (form: `image`, `human_prompt`) |

### X-Ray Service — `:8002`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/models` | Available models info |
| `POST` | `/analyze/xray` | Analyze X-ray (`file`, `confidence_threshold`) |

### Web Search — `:8003`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/chat` | Search query `{prompt}` |

---

## Project Structure

```
tammeny/
├── rag_chatbot.py          ← Chatbot API (port 8000)
├── Live_MedProc.py         ← Vision AI API (port 8001)
├── main.py                 ← Web-search API (port 8003)
├── chatbot_ui.html         ← Bilingual single-page UI
├── .env.example            ← API key template
├── requirements.txt
│
├── service/imaging-service/
│   ├── server.py           ← Imaging API (port 8002)
│   ├── inference.py        ← Inference pipeline
│   ├── postproc.py         ← Result formatter
│   ├── Dockerfile
│   └── models/xray_model/
│       ├── xray_analyzer.py
│       ├── model_loader.py
│       └── nih_processor.py
│
└── docs/
    └── screenshots/
        ├── chat_eng.png
        ├── xray_high.png
        └── xray_low.png
```

---

## Disclaimer

This is a demonstration project built for educational purposes. It is **not** intended for clinical use and is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical decisions.

---