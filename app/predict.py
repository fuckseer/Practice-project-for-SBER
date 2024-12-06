from __future__ import annotations

import io
from io import StringIO
from typing import TYPE_CHECKING

import pandas as pd
from PIL import Image
from s3 import BUCKET_OBJECTS_URL, s3_client, s3_resource

if TYPE_CHECKING:
    from ultralytics import YOLO
    from ultralytics.engine.results import Results


def __retrieve_images_urls(s3_bucket: str, import_id: str) -> list[str]:
    # Получаем список всех объектов в бакете внутри директории import_id
    response = s3_client.list_objects_v2(Bucket=s3_bucket, Prefix=import_id)
    if "Contents" not in response:
        return []

    # Конструируем URL до объектов в директории.
    # Так как при фильтрации Prefix'ом, путь до самой import_id директории
    # тоже возвращается после list_objects_v2(),
    # исключаем её из результирующего списка.
    return [
        f"{BUCKET_OBJECTS_URL}/{item['Key']}"
        for item in response["Contents"]
        if item["Key"] != import_id and item.get("Size", 1) > 0
    ]


def __generate_dataframe(
    urls: list[str], processed_data_batch: list[Results]
) -> pd.DataFrame:
    # Данные для построения DataFrame
    data = []
    # image_data представляет из себя объект типа Results
    for url, image_data in zip(urls, processed_data_batch):
        # У Results есть поля path и boxes,
        # хранящие пути до файлов и найденные YOLO боксы.
        name = url.split("/")[-1]
        # Будем сохранять нормированные боксы в формате x1y1x2y2.
        boxes = image_data.boxes.xyxyn
        # Заполняем список данными для DataFrame, по схеме предполагаемой CSV.
        for box in boxes:
            data.append(
                {"photo": name, "boxes": ", ".join(map(str, box.tolist()))}
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


def __choose_images(processed_data_batch: list[Results]) -> list[(str, bytes)]:
    result = []
    for image_data in processed_data_batch:
        name = image_data.path
        encoded_image = Image.fromarray(image_data.plot())
        result_image_bytes = io.BytesIO()
        encoded_image.save(result_image_bytes, format="PNG")
        result.append((name, result_image_bytes.getvalue()))

    return result


def __upload_images_to_s3(
    s3_bucket: str, task_id: str, images: list[(str, bytes)]
):
    for name, data in images:
        s3_resource.Object(s3_bucket, f"{task_id}/{name}").put(Body=data)


def predict(model: YOLO, s3_bucket: str, import_id: str, task_id: str):
    """Функция распознания мусора на изображениях.

    Получает изображения из s3://{s3_bucket}/{import_id}.
    Результаты загружаются в s3://{s3_bucket}/{task_id}.
    """
    # Получаем список URL к изображениям на S3.
    images_urls = __retrieve_images_urls(s3_bucket, import_id)
    # Отправляем изображения на обработку модели.
    results = model.predict(images_urls)
    # Отправляем на генерацию итогового DataFrame для отчёта.
    results_data_frame = __generate_dataframe(images_urls, results)
    # Начинаем загрузку DataFrame на S3, в формате CSV.
    __upload_processed_dataframe(results_data_frame, s3_bucket, task_id)

    example_images = __choose_images(results)
    __upload_images_to_s3(s3_bucket, task_id, example_images)
