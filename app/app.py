from __future__ import annotations

import os
import uuid
from io import StringIO
from pathlib import Path

import boto3
import mlflow
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse
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

def predict_mock(yolo_model, s3_bucket, import_id, task_id):
    """Шаблон функции распознания."""
    for obj in s3_bucket.objects.filter(Prefix=import_id).limit(10):
        value = s3.Object(BUCKET_NAME, obj.key).get()["Body"].read()
        s3.Object(
            BUCKET_NAME,
            str(Path(task_id) / Path(obj.key).name)
        ).put(Body=value)

    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3.Object(
        BUCKET_NAME,
        str(Path(task_id) / "result.csv")
    ).put(Body=csv_buffer.getvalue())

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


@app.get("/api/import/status/{import_id}")
def import_status(import_id: str):
    """Проверка статуса импорта."""
    return {"status": "ready"}


@app.post("/api/predict/{import_id}")
def predict(import_id: str):
    """Распознание импортированных изображений."""
    task_id = str(uuid.uuid4())
    predict_mock(model, bucket, import_id, task_id)
    return {"task_id": task_id}


@app.get("/api/predict/status/{task_id}")
def predict_status(task_id: str):
    """Проверка статуса распознания."""
    return {"status": "ready"}


@app.post("/api/results/{task_id}")
def results(task_id: str):
    """Получение результатов распознания."""
    return {"csv": "http://", "images": ["http://"]}
