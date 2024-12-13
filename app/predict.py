from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

import cv2
<<<<<<< Updated upstream
=======
import boto3
import os
import re
>>>>>>> Stashed changes
import pandas as pd
from model import MODEL_CONF
from sqlmodel import select, Session, create_engine
from db_models import S3Credentials
from s3 import BUCKET_OBJECTS_URL, s3_client, s3_resource

if TYPE_CHECKING:
    from ultralytics import YOLO
    from ultralytics.engine.results import Results 

DB_CONNECTION_STRING = os.getenv("POSTGRESQL_CONNECTION_STRING", "")
engine = create_engine(DB_CONNECTION_STRING)


<<<<<<< Updated upstream
def __retrieve_images_urls(s3_bucket: str, import_id: str) -> list[str]:
    # Получаем список всех объектов в бакете внутри директории import_id
    response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=import_id)
=======
def __format_GPS(full_gps: str) -> str:
    """Форматирование ExifTags.IFD.GPSInfo строки в строку формата GPS координат:
    'dd°mm'ss"(N/S) dd°mm'ss"(W/E)' с градусами, минутами и секундами.

    Args:
        full_gps: Строковое представление словаря ExifTags.IFD.GPSInfo значений.

    Returns:
        Форматированная строка, представляющая GPS координаты в градусах, минутах, секундах с направлением,
        или переданную строку, в случае ошибки форматирования.
    
    ## Example:
    full_gps = {1: 'N', 2: (4.0, 0.0, 36.6771599), 3: 'W', 4: (25.0, 58.0, 54.73848), 5: b'\x00', 6: 19.153, 7: (13.0, 50.0, 13.0), 29: '2022:03:15'};\n
    output = 4°00'36.7"N 25°58'54.7"W
    """
    pattern = r"\{1: '([NS])', 2: \((\d+)\.\d+, (\d+)\.\d+, (\d+\.\d+)\), 3: '([EW])', 4: \((\d+)\.\d+, (\d+)\.\d+, (\d+\.\d+)\)"
    match = re.search(pattern, full_gps)
    if not match:
        # Если совпадений по регулярке нет - значит исходные данные о GPS
        # отсутствовали, либо были неполные (отсутствовали ширина и долгота).
        return full_gps
    # Извлекаем значения ширины и долготы.
    lat_dir, lat_deg, lat_min, lat_sec = match.group(1), int(match.group(2)), int(match.group(3)), float(match.group(4))
    lon_dir, lon_deg, lon_min, lon_sec = match.group(5), int(match.group(6)), int(match.group(7)), float(match.group(8))
    
    def format_dms(degrees, minutes, seconds, direction):
        """Приводит к обозначеному формату"""
        return f"{degrees}°{minutes:02}'{seconds:.1f}\"{direction}"
    
    formatted_coordinates = (
        f"{format_dms(lat_deg, lat_min, lat_sec, lat_dir)} "
        f"{format_dms(lon_deg, lon_min, lon_sec, lon_dir)}"
    )
    return formatted_coordinates


def __retrieve_metadata(s3_bucket: str, obj_key: str) -> str:
    head = s3_client.head_object(Bucket=s3_bucket, Key=obj_key)
    metadata = head['Metadata']
    GPS_metadata = metadata['Gps']
    if GPS_metadata:
        formatted_GPS = __format_GPS(GPS_metadata)
        return formatted_GPS
    return ""


def __retrieve_images_urls_with_metadata(
        s3_bucket: str, import_id: str, from_cloud: bool=False, s3_cloud_credentials=None
) -> dict[str, str]:
    if not from_cloud:
        # Получаем список всех объектов в бакете внутри директории import_id
        response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=import_id)
    else:
        # Получаем папку из пути {bucket}/{folder}
        folder = s3_cloud_credentials.s3_path_to_folder.split("/")[1]
        response = boto3.client(
            's3',
            endpoint_url=s3_cloud_credentials.endpoint_url,
            aws_access_key_id=s3_cloud_credentials.access_key,
            aws_secret_access_key=s3_cloud_credentials.secret_key
        ).list_objects_v2(Bucket=s3_bucket, Prefix=folder)


>>>>>>> Stashed changes
    if "Contents" not in response:
        return []

    # Конструируем URL до объектов в директории.
    # Так как при фильтрации Prefix'ом, путь до самой import_id директории
    # тоже возвращается после list_objects_v2(),
    # исключаем её из результирующего списка.
<<<<<<< Updated upstream
    return [
        f"{BUCKET_OBJECTS_URL}/{item['Key']}"
        for item in response["Contents"]
        if item["Key"] != import_id and item.get("Size", 1) > 0
    ]
=======
    data = {}
    for item in response['Contents']:
        if item['Key'] != import_id and item.get("Size", 1) > 0:
            metadata = __retrieve_metadata(s3_bucket, item['Key'])
            if not from_cloud:
                url = f"{BUCKET_OBJECTS_URL}/{item['Key']}"
            else:
                url = f"{s3_cloud_credentials.endpoint_url}/{s3_bucket}/{item['Key']}"
            data[url] = metadata
    return data
>>>>>>> Stashed changes


def __generate_dataframe(
    urls: list[str], processed_data_batch: list[Results]
) -> pd.DataFrame:
    # Данные для построения DataFrame
    data = []
    # image_data представляет из себя объект типа Results
    for url, image_data in zip(urls, processed_data_batch):
        # У Results есть поле boxes, хранящее найденные YOLO боксы.
        name = url.split("/")[-1]
        # Будем сохранять нормированные боксы в формате x1y1x2y2.
        boxes = image_data.boxes.xyxyn
        # Заполняем список данными для DataFrame, по схеме предполагаемой CSV.
        for box in boxes:
            x1, y1, x2, y2 = box.tolist()
            data.append(
                {"photo": name, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
            )

    return pd.DataFrame(data)


def __upload_processed_dataframe(
    df: pd.DataFrame, s3_bucket: str, task_id: str
):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_resource.Object(s3_bucket, f"{task_id}/result.csv").put(
        Body=csv_buffer.getvalue()
    )


def __render_image(image_data: Results) -> bytes:
    arr = image_data.plot()
    _, img_encoded = cv2.imencode(".jpg", arr)
    return img_encoded.tobytes()


def __choose_images(processed_data_batch: list[Results]) -> list[(str, bytes)]:
    result = []
    for image_data in processed_data_batch:
        name = image_data.path
        result.append((name, __render_image(image_data)))

    return result


def __upload_images_to_s3(
    s3_bucket: str, task_id: str, images: list[(str, bytes)]
):
    for name, data in images:
        s3_resource.Object(s3_bucket, f"{task_id}/{name}").put(Body=data)


def predict_local(model: YOLO, s3_bucket: str, import_id: str, task_id: str):
    """Функция распознания мусора на изображениях.

    Получает изображения из s3://{s3_bucket}/{import_id}.
    Результаты загружаются в s3://{s3_bucket}/{task_id}.
    """
    # Получаем список URL к изображениям на S3.
    images_urls = __retrieve_images_urls(s3_bucket, import_id)
    # Отправляем изображения на обработку модели.
    results = model.predict(images_urls, conf=MODEL_CONF)
    # Отправляем на генерацию итогового DataFrame для отчёта.
    results_data_frame = __generate_dataframe(images_urls, results)
    # Начинаем загрузку DataFrame на S3, в формате CSV.
    __upload_processed_dataframe(results_data_frame, s3_bucket, task_id)

    example_images = __choose_images(results)
    __upload_images_to_s3(s3_bucket, task_id, example_images)


def predict_cloud(model: YOLO, s3_our_bucket: str, import_id: str, task_id: str):
    """Функция распознания мусора на изображениях.

    Получает изображения из s3://{s3_cloud_bucket}/{import_id}.
    Результаты загружаются в s3://{s3_our_bucket}/{task_id}.
    """
    with Session(engine) as session:
        query = select(S3Credentials).where(S3Credentials.id == import_id)
        s3_credentials = session.exec(query).first()
        if not s3_credentials:
            raise Exception(f'{s3_credentials} instance not found in DB.')
    
    cloud_bucket = s3_credentials.s3_path_to_folder.split("/")[0]
    # Получаем словарь {URL : Метаданные} изображений на S3.
    images_data = __retrieve_images_urls_with_metadata(
        cloud_bucket, 
        import_id,
        from_cloud=True,
        s3_cloud_credentials=s3_credentials
    )
    # Извлекаем URLs.
    images_urls = list(images_data.keys())
    # Отправляем изображения на обработку модели.
    results = model.predict(images_urls, conf=MODEL_CONF)
    # Отправляем на генерацию итогового DataFrame для отчёта.
    results_data_frame = __generate_dataframe(
        images_urls,
        images_data, 
        results
    )
    # Начинаем загрузку DataFrame на S3, в формате CSV.
    __upload_processed_dataframe(results_data_frame, s3_our_bucket, task_id)

    example_images = __choose_images(results)
    __upload_images_to_s3(s3_our_bucket, task_id, example_images)
