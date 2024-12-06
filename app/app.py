from __future__ import annotations

import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, Response, UploadFile
from fastapi.responses import HTMLResponse
from model import model
from predict import predict_mock
from s3 import BUCKET_NAME, BUCKET_OBJECTS_URL, bucket, s3

load_dotenv()

app = FastAPI()

APP_URL = os.getenv("APP_URL", "http://localhost:7860")
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
        bucket.upload_fileobj(image.file, f"{import_id}/{image.filename}")
    return {"import_id": import_id}


def __folder_exists(key):
    return True


@app.get("/api/import/status/{import_id}")
def import_status(import_id: str):
    """Проверка статуса импорта."""
    exists = __folder_exists(import_id)
    return (
        {"status": "ready"}
        if exists
        else Response({"status": "in process"}, 204)
    )


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
    return (
        {"status": "ready"}
        if exists
        else Response({"status": "in process"}, 204)
    )


def __not_csv(key):
    ext = key.split(".")[-1]
    return ext != "csv"


def __get_task_images(task_id, max_count):
    objects = bucket.objects.filter(Prefix=task_id).limit(max_count + 1)
    return [obj for obj in objects if __not_csv(obj.key)][:max_count]


@app.get("/api/results/{task_id}")
def results(task_id: str):
    """Получение результатов распознания."""
    base_url = BUCKET_OBJECTS_URL
    csv_url = f"{base_url}/{task_id}/result.csv"
    image_urls = []
    for image in __get_task_images(task_id, 10):
        image_urls.append(f"{base_url}/{image.key}")
    return {"csv": csv_url, "images": image_urls}
