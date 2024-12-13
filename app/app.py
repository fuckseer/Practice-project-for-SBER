from __future__ import annotations

import os
import uuid

<<<<<<< Updated upstream
from dotenv import load_dotenv
from fastapi import FastAPI, Response, UploadFile
=======
import boto3
from io import BytesIO
from typing import Annotated
from dotenv import load_dotenv
from fastapi import FastAPI, Response, UploadFile, HTTPException, Depends
from PIL import Image, ExifTags
>>>>>>> Stashed changes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from model import model
from predict import predict_local, predict_cloud
from contextlib import asynccontextmanager
from s3 import BUCKET_NAME, BUCKET_OBJECTS_URL, bucket
from db_models import S3Request, S3Credentials
from sqlmodel import SQLModel, Session, create_engine
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

load_dotenv()


APP_URL = os.getenv("APP_URL", "http://localhost:7860")
ALLOWED_URLS = os.getenv("ALLOWED_URLS", "http://localhost:3000").split(",")
DB_CONNECTION_STRING = os.getenv("POSTGRESQL_CONNECTION_STRING", "")


root_page = f"""
<html>
    <body>
        <h1>
            Привет! Используй API по адресу <a href="{APP_URL}">{APP_URL}</a>
        </h1>
    </body>
</html>
"""


@asynccontextmanager
async def db_create_lifespan_event(app: FastAPI):
    # Выполнится перед началом работы приложения.
    # Используется взамен устаревшего on.startup()
    # https://fastapi.tiangolo.com/advanced/events/#lifespan-function
    __create_db_and_tables()
    yield


app = FastAPI(lifespan=db_create_lifespan_event)
engine = create_engine(DB_CONNECTION_STRING)


# Разрешаем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_URLS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def __create_db_and_tables():
    SQLModel.metadata.create_all(engine)


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


@app.post("/api/import/cloud")
def import_cloud(request: S3Request):
    import_id = str(uuid.uuid4())
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=request.endpoint_url,
            aws_access_key_id=request.access_key,
            aws_secret_access_key=request.secret_key
        )
        # Проверка доступа к бакету.
        bucket_name = request.s3_path_to_folder.split("/")[0]
        # Для выполнения list_objects_v2(Bucket=bucket_name) нужны права на чтение.
        # Не скачивает файлы.
        s3_client.list_objects_v2(Bucket=bucket_name)
    except (NoCredentialsError, PartialCredentialsError):
        raise HTTPException(status_code=400, detail='Неверные учетные данные AWS.')
    except ClientError as e:
        raise HTTPException(status_code=400, detail=f'Ошибка соединения с S3: {e.response}')
    
    with Session(engine) as session:
        existing_entry = session.query(
            S3Credentials
        ).filter(S3Credentials.s3_path_to_folder == request.s3_path_to_folder).first()
        if existing_entry:
            #TODO: Обработать поведение, когда одна и та же ссылка передается снова.
            # Если данные уже обработаны, то лучше возвращаться ссылку на готовый эксперимент
            # (Ссылка с query params значениями, пока не реализована).
            raise HTTPException(status_code=400, detail='Запись об этих данных уже сохранялась.')
        
        credentials_entry = S3Credentials(
            id=import_id,
            s3_path_to_folder=request.s3_path_to_folder,
            endpoint_url=request.endpoint_url,
            access_key=request.access_key,
            secret_key=request.secret_key
        )
        session.add(credentials_entry)
        session.commit()
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
def predict_images(import_id: str):
    """Распознание импортированных изображений."""
    task_id = str(uuid.uuid4())
    predict_local(model, BUCKET_NAME, import_id, task_id)
    return {"task_id": task_id}


@app.post("/api/predict_cloud/{import_id}")
def predict_images(import_id: str):
    """Распознание изображений сохраненных на S3."""
    task_id = str(uuid.uuid4())
    predict_cloud(model, BUCKET_NAME, import_id, task_id)
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
