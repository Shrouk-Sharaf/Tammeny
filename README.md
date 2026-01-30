# Healthcare AI System

A comprehensive AI-powered healthcare platform providing medical image analysis, intelligent chatbots, OCR processing, and a user-friendly web interface for medical professionals and patients.

## Features

- **Medical Image Analysis**: AI-powered X-ray analysis using deep learning models
- **Intelligent Chatbot**: RAG-based conversational AI for medical queries with PDF document support
- **OCR Service**: Optical character recognition for medical documents
- **LLM Proxy**: Secure proxy for large language model interactions
- **Web UI**: Modern Streamlit-based interface for easy access
- **Microservices Architecture**: Scalable, containerized services

## Architecture

The system consists of the following microservices:

- **API Service** (`services/api/`): Main FastAPI backend
- **Imaging Service** (`services/imaging-service/`): Medical image analysis (port 8002)
- **LLM Proxy** (`services/llm-proxy/`): Language model proxy service
- **OCR Service** (`services/ocr-service/`): Document text extraction
- **Streamlit UI** (`services/streamlit-ui/`): Web interface (port 8501)
- **Chatbot API** (`rag_chatbot.py`): RAG-based chatbot (port 8502)

## Prerequisites

- Python 3.8+
- Docker (optional, for containerized deployment)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd healthcare-ai
```

2. Install dependencies for each service:

### Imaging Service
```bash
cd services/imaging-service
pip install -r requirements.txt
```

### Chatbot API
```bash
pip install fastapi uvicorn langchain langchain-community langchain-text-splitters langchain-huggingface faiss-cpu sentence-transformers langchain-mistralai pypdf
```

### Streamlit UI
```bash
cd services/streamlit-ui
pip install -r requirements.txt
```

### Live Medical Procedure API
```bash
pip install fastapi uvicorn requests python-multipart
```

## Configuration

⚠️ **Security Note**: The codebase contains hardcoded API keys for demonstration purposes. For production use:

1. Create a `.env` file based on `.env.example`
2. Replace all hardcoded API keys with environment variables
3. Use secure key management (e.g., AWS Secrets Manager, Azure Key Vault)

## Running the Application

### Local Development

1. **Start Imaging Service** (Terminal 1):
```bash
cd services/imaging-service
python server.py
```

2. **Start Chatbot API** (Terminal 2):
```bash
python rag_chatbot.py
```

3. **Start Streamlit UI** (Terminal 3):
```bash
cd services/streamlit-ui
streamlit run app.py
```

4. **(Optional) Start Live Medical Procedure API** (Terminal 4):
```bash
uvicorn Live_MedProc:app --reload --host 127.0.0.1 --port 8001
```

### Docker Deployment

Build and run each service individually:

```bash
# Imaging Service
cd services/imaging-service
docker build -t healthcare-imaging .
docker run -p 8002:8002 healthcare-imaging

# API Service
cd services/api
docker build -t healthcare-api .
docker run -p 8000:8000 healthcare-api

# And so on for other services...
```

## Usage

1. Open your browser and navigate to `http://localhost:8501`
2. Use the X-ray Analyzer to upload medical images for AI analysis
3. Interact with the Healthcare Assistant Chatbot for medical queries
4. Upload PDF documents to enhance chatbot responses with specific medical knowledge

## API Endpoints

### Imaging Service (Port 8002)
- `GET /`: Service health check
- `GET /models`: Available imaging models
- `POST /analyze/xray`: Analyze X-ray images
- `GET /health`: Health check

### Chatbot API (Port 8502)
- `GET /`: Serve HTML interface
- `POST /load_pdf/`: Upload and process PDF documents
- `POST /chat`: Chat with the AI assistant

### Live Medical Procedure API (Port 8001)
- `POST /analyze_image/`: Analyze medical images using external AI

## Development

### Project Structure
```
healthcare-ai/
├── services/
│   ├── api/                 # Main API service
│   ├── imaging-service/     # Medical imaging analysis
│   ├── llm-proxy/          # LLM proxy service
│   ├── ocr-service/        # OCR processing
│   └── streamlit-ui/       # Web interface
├── Live_MedProc.py         # Image analysis API
├── main.py                 # Basic chatbot
├── rag_chatbot.py          # RAG chatbot
├── rag+fastapi.py          # Colab version
├── Rag+fastapi.ipynb       # Jupyter notebook
├── chatbot_ui.html         # HTML interface
└── README.md
```

### Adding New Features

1. Create a new service in the `services/` directory
2. Add a Dockerfile for containerization
3. Update the main README with new endpoints
4. Ensure proper CORS configuration for cross-service communication

## Testing

Run individual service tests:

```bash
# Imaging service health check
curl http://localhost:8002/health

# Chatbot API test
curl -X POST "http://localhost:8502/chat" -H "Content-Type: application/json" -d '{"prompt": "What are symptoms of flu?", "session_id": "test"}'
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This is a demonstration project for educational purposes. It is not intended for clinical use or as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical decisions.

## Contact

For questions or support, please open an issue in the repository.
