from __future__ import annotations

import os
from io import StringIO

import boto3
import pandas as pd
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

resource = boto3.resource(
    "s3",
    endpoint_url="https://storage.yandexcloud.net",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
)

s3_client = boto3.client(
    "s3",
    endpoint_url="https://storage.yandexcloud.net",
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
)


def retrieve_images_urls(s3_bucket, import_id) -> list[str]:
    # Получаем список всех объектов в бакете внутри директории import_id
    response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=import_id)
    if "Contents" not in response:
        return []

    # Конструируем URL до объектов в директории. Так как при фильтрации Prefix'ом,
    # путь до самой import_id директории тоже возвращается после list_objects_v2(),
    # исключаем её из результирующего списка.
    files_urls = [
        f"https://storage.yandexcloud.net/{s3_bucket}/{item['Key']}"
        for item in response["Contents"]
        if item["Key"] != import_id and item.get("Size", 1) > 0
    ]
    return files_urls


def generate_dataframe(urls, processed_data_batch):
    # Данные для построения DataFrame
    data = []
    # image_data представляет из себя объект типа Results
    for url, image_data in zip(urls, processed_data_batch):
        # У Results есть поля path и boxes, хранящие пути до файлов и найденные YOLO боксы.
        name = url.split("/")[-1]
        # Будем сохранять нормированные боксы в формате x1y1x2y2.
        boxes = image_data.boxes.xyxyn
        # Заполняем список данными для DataFrame, по схеме предполагаемой CSV.
        for box in boxes:
            data.append(
                {"photo": name, "boxes": ", ".join(map(str, box.tolist()))}
            )

    df = pd.DataFrame(data)

    # Для локального сохранения CSV файла.
    # df.to_csv("report.csv", index=False)

    return df


def upload_processed_dataframe(df: pd.DataFrame, s3_bucket, task_id):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    resource.Object(s3_bucket, f"{task_id}/result.csv").put(
        Body=csv_buffer.getvalue()
    )


def process(model: YOLO, s3_bucket, import_id, task_id):
    # Получаем список URL к изображениям на S3.
    images_urls = retrieve_images_urls(s3_bucket, import_id)
    # Отправляем изображения на обработку модели.
    results = model.predict(images_urls)
    # Отправляем на генерацию итогового DataFrame для отчёта.
    results_data_frame = generate_dataframe(images_urls, results)
    # Начинаем загрузку DataFrame на S3, в формате CSV.
    upload_processed_dataframe(results_data_frame, s3_bucket, task_id)


# Необходимые для процессинга тестовые данные.
model_test = YOLO(".models/best/best.pt")
example_import_id = "backend-example-import-id"
example_task_id = "backend-example-task-id-1"

# Запуск проверочной проходки.
process(
    model=model_test,
    s3_bucket="waste",
    import_id=example_import_id,
    task_id=example_task_id,
)
