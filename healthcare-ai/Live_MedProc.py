import os
import base64
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import requests

app = FastAPI(title="Medical Image Chatbot API")

API_URL = "https://router.huggingface.co/v1/chat/completions"
HEADERS = {
    "Authorization": "Bearer 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"
}

MODEL_NAME = "Qwen/Qwen2.5-VL-7B-Instruct:hyperbolic"


@app.post("/analyze_image/")
async def analyze_image(
    image: UploadFile = File(...),
    human_prompt: str = Form("Describe the medical condition in this image.")
):
    """
    Upload an image + user question and send to Qwen medical AI model.
    """

    try:
        # Read image and convert to Base64
        img_bytes = await image.read()
        img_b64 = base64.b64encode(img_bytes).decode()

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional medical AI assistant. "
                               "You analyze medical images, identify abnormalities, "
                               "describe severity, and provide medical explanations."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": human_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}"
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={"error": response.text}
            )

        result = response.json()
        output = result["choices"][0]["message"]

        return {"response": output}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Run server with:
# uvicorn filename:app --reload
