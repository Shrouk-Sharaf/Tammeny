# 🩺 Tammeny — طمّني

> **AI-Powered Healthcare Communication**  

Tammeny bridges the gap between complex medical AI and real patient understanding — with plain-language explanations, document Q&A, and intelligent health guidance in Arabic and English.

---

## Features

| Feature | Description |
|---|---|
| **X-Ray Analyzer** | DenseNet-121 (NIH ChestX-ray14) — screens for 14 thoracic conditions with plain-language results |
| **Vision AI** | Upload any medical image, ask a question, get a patient-friendly explanation (Qwen2.5-VL) |
| **Health Assistant** | RAG chatbot with conversation memory, PDF document Q&A, Arabic & English support |
| **Bilingual UI** | Full Arabic ↔ English toggle with RTL layout support |

---

## Project Structure

```
tammeny/
├── rag_chatbot.py          ← Chatbot API (port 8000)
├── Live_MedProc.py         ← Vision AI API (port 8001)
├── chatbot_ui.html         ← Standalone chatbot HTML UI
├── main.py                 ← Web-search chatbot (optional)
├── .env.example            ← Environment variable template
├── requirements.txt

│
├── imaging-service/
│   ├── server.py           ← Imaging API (port 8002)
│   ├── inference.py        ← Inference pipeline
│   ├── postproc.py         ← Result formatter
│   ├── Dockerfile
│   └── models/xray_model/
│       ├── xray_analyzer.py
│       ├── model_loader.py
│       └── nih_processor.py
│
```

---

## Setup

### 1. Clone & Configure

```bash
git clone https://github.com/Shrouk-Sharaf/Tammeny
cd Tammeny
cp .env.example .env
# Edit .env and fill in your API keys
```

### 2. Install Dependencies

```bash
# Root dependencies (chatbot + vision)
pip install fastapi uvicorn python-multipart langchain langchain-community \
    langchain-text-splitters langchain-huggingface langchain-mistralai \
    faiss-cpu sentence-transformers pypdf python-dotenv requests

# Imaging service
cd imaging-service
pip install -r requirements.txt
cd ..

```

---

## Running

Open **3 terminals**:

```bash
# Terminal 1 — Chatbot API
python rag_chatbot.py
# → http://127.0.0.1:8000

# Terminal 2 — Vision AI
uvicorn Live_MedProc:app --reload --host 127.0.0.1 --port 8001
# → http://127.0.0.1:8001

# Terminal 3 — Imaging Service
cd imaging-service && python server.py
# → http://0.0.0.0:8002

# Terminal 4 (optional) — Web-search chatbot
python main.py
# → http://0.0.0.0:8003
```


Then use the APIs:
- `http://127.0.0.1:8000/` (chatbot)
- `http://127.0.0.1:8001/` (vision)
- `http://127.0.0.1:8002/health` (xray health)
- `http://0.0.0.0:8003/` (web-search chatbot)

Alternative (single command): `.\run_all.ps1` (PowerShell).

---

## API Keys Needed

| Key | Where to Get |
|---|---|
| `MISTRAL_API_KEY` | https://console.mistral.ai/ — free tier available |
| `HUGGINGFACEHUB_API_TOKEN` | https://huggingface.co/settings/tokens — free |
| `HF_ROUTER_TOKEN` | Same HuggingFace token |

---

## Docker (Optional)

```bash
# Imaging service
cd imaging-service
docker build -t tammeny-imaging .
docker run -p 8002:8002 tammeny-imaging
```
docker run -p 8501:8501 tammeny-ui
```

---

## API Reference

### Chatbot (`:8000`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serve chatbot HTML UI |
| POST | `/load_pdf/` | Upload PDF for RAG context |
| POST | `/chat` | Chat (body: `{prompt, session_id}`) |

### Vision AI (`:8001`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/analyze_image/` | Analyze image (form: `image`, `human_prompt`) |

### Imaging (`:8002`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/models` | Available models |
| POST | `/analyze/xray` | Analyze X-ray (file + `confidence_threshold`) |

### Web-search Chatbot (`:8003`)    
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/chat` | Chat with web search (body: `{prompt, session_id}`) |


=======
### Live Medical Procedure API (Port 8001)
- `POST /analyze_image/`: Analyze medical images using external AI

## Development

### Adding New Features

1. Create a new service in the `services/` directory
2. Add a Dockerfile for containerization
3. Update the main README with new endpoints
4. Ensure proper CORS configuration for cross-service communication


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Disclaimer

This is a demonstration project for educational purposes. It is not intended for clinical use or as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical decisions.