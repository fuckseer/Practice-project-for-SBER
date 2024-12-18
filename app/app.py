from __future__ import annotations

import os
import re
import uuid

import boto3
from dotenv import load_dotenv
from fastapi import FastAPI, Response, UploadFile, HTTPException, Depends
from PIL import Image, ExifTags
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from model import model
from predict import predict_local, predict_cloud
from contextlib import asynccontextmanager
from regex_patterns import PARSE_S3_COMPONENTS_PATTERN
from s3 import BUCKET_NAME, BUCKET_OBJECTS_URL, bucket
from db_models import S3Request, S3ClientData
from sqlmodel import SQLModel, Session, create_engine, select
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


def __extract_gps_metadata(image_content) -> str:
    try:
        exif_data = image_content.getexif()
        gps_ifd = exif_data.get_ifd(ExifTags.IFD.GPSInfo)
        if not gps_ifd:
            return ''
        return str(gps_ifd)
    except Exception as e:
        print(f'Error occured: {e}')
        return ''


def __extract_subdirectories_path(
        full_path: str,
        endpoint: str,
        bucket: str,
        final_folder: str
) -> str:
    """Извлекает путь между bucket и до final_folder"""
    start_marker = f"{endpoint}/{bucket}/"
    end_marker = f"/{final_folder}"

    start_idx = full_path.find(start_marker) + len(start_marker)
    end_idx = full_path.find(end_marker)
    
    return full_path[start_idx:end_idx]


@app.post("/api/import/local")
def import_local(images: list[UploadFile]):
    """Импорт нескольких изображений."""
    import_id = str(uuid.uuid4())
    for image in images:
        try:
            image_content = Image.open(image.file)
            gps_metadata = __extract_gps_metadata(image_content)
            image.file.seek(0)
            bucket.upload_fileobj(
                image.file, 
                f"{import_id}/{image.filename}",
                ExtraArgs={'Metadata': {'Gps': gps_metadata}}
            )
        except Exception as e:
            return {'Failed to upload: ': f'{image.filename} with error {str(e)}'}
    return {"import_id": import_id}


@app.post("/api/import/cloud")
def import_cloud(request: S3Request):
    try:
        match = re.match(PARSE_S3_COMPONENTS_PATTERN, request.s3_path_to_folder)
        if match:
            endpoint_url = match.group(1)
            bucket_name = match.group(2)
            folder_to_predict_from = match.group(4)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Неверный формат S3 URL: {request.s3_path_to_folder}. Ожидаемый формат: https://endpoint_url/bucket/.../folder"
            )
        
        # Проверка доступа к бакету.
        # Для выполнения list_objects_v2(Bucket=bucket_name) нужны права на чтение.
        # Не скачивает файлы.
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=request.access_key,
            aws_secret_access_key=request.secret_key
        )
        s3_client.list_objects_v2(Bucket=bucket_name)
    except (NoCredentialsError, PartialCredentialsError):
        raise HTTPException(status_code=400, detail='Неверные учетные данные S3.')
    except ClientError as e:
        raise HTTPException(status_code=400, detail=f'Ошибка соединения с S3: {e.response}')
    
    with Session(engine) as session:
        existing_entry = session.exec(
            select(S3ClientData)
            .where(S3ClientData.full_path == request.s3_path_to_folder)
        ).first()
        if existing_entry:
            #TODO: Обработать поведение, когда одна и та же ссылка передается снова.
            # Если данные уже обработаны, то лучше возвращаться ссылку на готовый эксперимент
            # (Ссылка с query params значениями, пока не реализована).
            raise HTTPException(status_code=400, detail='Запись об этих данных уже сохранялась.')
        
        import_id = str(uuid.uuid4())
        full_path=request.s3_path_to_folder
        access_key=request.access_key
        secret_key=request.secret_key
        # Извлекаем путь между бакетом и до конечной папки.
        subdirectories_path = __extract_subdirectories_path(
            full_path=full_path,
            endpoint=endpoint_url,
            bucket=bucket_name,
            final_folder=folder_to_predict_from
        )
        # Создаем запись в БД.
        credentials_entry = S3ClientData(
            id=import_id,
            full_path=full_path,
            subdirectories_path=subdirectories_path,
            folder=folder_to_predict_from,
            bucket=bucket_name,
            endpoint_url=endpoint_url,
            access_key=access_key,
            secret_key=secret_key
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
