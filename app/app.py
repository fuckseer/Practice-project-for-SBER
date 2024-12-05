from __future__ import annotations

import os
import uuid
from pathlib import Path

import boto3
import mlflow
from dotenv import load_dotenv
from fastapi import FastAPI, Response, UploadFile
from fastapi.responses import HTMLResponse
from predict import predict_mock
from ultralytics import YOLO

load_dotenv()

app = FastAPI()

DOWNLOAD_MODEL = os.environ["DOWNLOAD_MODEL"].lower() == "true"
MLFLOW_URL = os.getenv("MLFLOW_URL", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "coco")
MODEL_TAG = os.getenv("MODEL_TAG", "best")
MODEL_PATH = f".models/{MODEL_TAG}"
APP_URL = os.getenv("APP_URL", "http://localhost:7860")
MLFLOW_S3_ENDPOINT_URL = os.getenv("MLFLOW_S3_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME", "waste")
BUCKET_OBJECTS_URL = os.getenv("BUCKET_OBJECTS_URL", "https://storage.yandexcloud.net/waste")

mlflow.set_tracking_uri(uri=MLFLOW_URL)

s3 = boto3.resource(
    "s3",
    endpoint_url=MLFLOW_S3_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
bucket = s3.Bucket(BUCKET_NAME)

def get_model(download_model: bool):  # noqa: FBT001
    """Функция, которая загружает модель."""
    if download_model:
        print("The model is loading...")
        mlflow.artifacts.download_artifacts(
            f"models:/{MODEL_NAME}@{MODEL_TAG}", dst_path=MODEL_PATH
        )
        print("The model is loaded.")
    return YOLO(f"{MODEL_PATH}/best.pt")


s3 = boto3.resource(
    "s3",
    endpoint_url=MLFLOW_S3_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

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


@app.post("/api/import/local")
def import_local(images: list[UploadFile]):
    """Импорт нескольких изображений."""
    import_id = str(uuid.uuid4())
    for image in images:
        bucket.upload_fileobj(
            image.file,
            str(Path(import_id) / image.filename)
        )
    return {"import_id": import_id}


def __folder_exists(key):
    return True


@app.get("/api/import/status/{import_id}")
def import_status(import_id: str):
    """Проверка статуса импорта."""
    exists = __folder_exists(import_id)
    return {"status": "ready"} if exists else \
        Response({"status": "in process"}, 204)


@app.post("/api/predict/{import_id}")
def predict(import_id: str):
    """Распознание импортированных изображений."""
    task_id = str(uuid.uuid4())
    predict_mock(model, s3, BUCKET_NAME, import_id, task_id)
    return {"task_id": task_id}


@app.get("/api/predict/status/{task_id}")
def predict_status(task_id: str):
    """Проверка статуса распознания."""
    exists = __folder_exists(task_id)
    return {"status": "ready"} if exists else \
        Response({"status": "in process"}, 204)


def __not_csv(key):
    return Path(key).suffix != "csv"


def __get_task_images(task_id, max_count):
    objects = bucket.objects.filter(Prefix=task_id).limit(max_count + 1)
    return [obj for obj in objects if __not_csv(obj.key)][:max_count]


@app.get("/api/results/{task_id}")
def results(task_id: str):
    """Получение результатов распознания."""
    base_url = Path(BUCKET_OBJECTS_URL)
    csv_url = base_url / task_id / "result.csv"
    image_urls = []
    for image in __get_task_images(task_id, 10):
        image_urls.append(base_url / image.key)
    return {"csv": csv_url, "images": image_urls}
