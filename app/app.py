import io
import os
from pathlib import Path

import mlflow
from dotenv import load_dotenv
from fastapi import FastAPI, Response, UploadFile
from PIL import Image
from ultralytics import YOLO

load_dotenv()

app = FastAPI()

# Константы
MODEL_NAME = "coco"
TAG = "best"
MODEL_PATH = f".models/{TAG}"
MLFLOW_URI = "http://waste.sergei-kiprin.ru:5000"
DOWNLOAD_MODEL = os.environ["DOWNLOAD_MODEL"].lower() == "true"

# Настройки MLFlow
mlflow.set_tracking_uri(uri=MLFLOW_URI)


# Загружаем модель
def get_model():
    if DOWNLOAD_MODEL:
        print("The model is loading...")
        mlflow.artifacts.download_artifacts(
            f"models:/{MODEL_NAME}@{TAG}", dst_path=MODEL_PATH
        )
        print("The model is loaded.")
    return YOLO(f"{MODEL_PATH}/best.pt")


model = get_model()


# Представление для предсказания от модели
@app.post("/predict")
def predict(image: UploadFile):
    image_bytes = image.file.read()
    pil_image = Image.open(io.BytesIO(image_bytes))
    result = model.predict(pil_image)
    encoded_image = Image.fromarray(result[0].plot())
    result_image_bytes = io.BytesIO()
    encoded_image.save(result_image_bytes, format="PNG")
    result_image_bytes = result_image_bytes.getvalue()
    return Response(content=result_image_bytes, media_type="image/png")
