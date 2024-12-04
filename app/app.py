import io
import os

import mlflow
from dotenv import load_dotenv
from fastapi import FastAPI, Response, UploadFile
from fastapi.responses import HTMLResponse
from PIL import Image
from ultralytics import YOLO

load_dotenv()

app = FastAPI()

# Константы
DOWNLOAD_MODEL = os.environ["DOWNLOAD_MODEL"].lower() == "true"
MLFLOW_URL = os.getenv("MLFLOW_URL", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "coco")
MODEL_TAG = os.getenv("MODEL_TAG", "best")
MODEL_PATH = f".models/{MODEL_TAG}"
APP_URL = os.getenv("APP_URL", "http://localhost:7860")

# Настройки MLFlow
mlflow.set_tracking_uri(uri=MLFLOW_URL)


# Загружаем модель
def get_model(download_model: bool):  # noqa: FBT001
    """Функция, которая загружает модель."""
    if download_model:
        print("The model is loading...")
        mlflow.artifacts.download_artifacts(
            f"models:/{MODEL_NAME}@{MODEL_TAG}", dst_path=MODEL_PATH
        )
        print("The model is loaded.")
    return YOLO(f"{MODEL_PATH}/best.pt")


model = get_model(DOWNLOAD_MODEL)

root_page = f"""
<html>
    <body>
        <h1>
            Привет! Используй API по адресу <a href="{APP_URL}">{APP_URL}</a>
        </h1>
    </body>
</html>
"""


@app.get("/")
def root():
    """Страница, возвращаемая по корню сайта."""
    return HTMLResponse(content=root_page, status_code=200)


@app.post("/predict")
def predict(image: UploadFile):
    """Конечная точка для получения предсказания от модели.

    Input: Изображение image
    Output: Изображение с выделенными боксами
    """
    image_bytes = image.file.read()
    pil_image = Image.open(io.BytesIO(image_bytes))
    result = model.predict(pil_image)
    encoded_image = Image.fromarray(result[0].plot())
    result_image_bytes = io.BytesIO()
    encoded_image.save(result_image_bytes, format="PNG")
    result_image_bytes = result_image_bytes.getvalue()
    return Response(content=result_image_bytes, media_type="image/png")
