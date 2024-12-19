import os
import dramatiq

from s3 import bucket
from io import BytesIO
from model import model
from datetime import datetime
from PIL import Image, ExifTags
from fastapi import HTTPException
from sqlmodel import Session, select
from predict import retrieve_images_urls_with_metadata, wrap_prediction
from db_models import engine, ImportImageJob, S3ClientData, PredictImageJob


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
    

@dramatiq.actor
def import_local(
    import_id: str,
    filepath: str,
    filename: str
) -> None:
    try:
        with open(filepath, "rb") as f:
            buffer = BytesIO(f.read())
            image_content = Image.open(buffer)   
            gps_metadata = __extract_gps_metadata(image_content)
            buffer.seek(0)
            bucket.upload_fileobj(
                buffer, 
                f"{import_id}/{filename}",
                ExtraArgs={'Metadata': {'Gps': gps_metadata}}
            )
            status = "completed"
    except Exception as e:
        status = "failed"
    finally:
        os.remove(filepath)
        with Session(engine) as session:
            statement = select(ImportImageJob).where(
                ImportImageJob.import_id == import_id,
                ImportImageJob.image_filename == filename
            )
            job = session.exec(statement).one()
            job.status = status
            job.updated_at = datetime.utcnow()
            session.add(job)            
            session.commit()


# @dramatiq.actor
# def predict_local(
#     s3_bucket: str, 
#     import_id: str, 
#     task_id: str
# ) -> None:
#     """Функция распознания мусора на изображениях.

#     Получает изображения из s3://{s3_bucket}/{import_id}.
#     Результаты загружаются в s3://{s3_bucket}/{task_id}.
#     """
#     try:
#         # Получаем словарь {URL : Метаданные} изображений на S3.
#         images_data = retrieve_images_urls_with_metadata(
#             import_id=import_id,
#             s3_bucket=s3_bucket
#         )
        
#         wrap_prediction(
#             model=model,
#             data=images_data,
#             s3_bucket=s3_bucket,
#             task_id=task_id
#         )
#     except Exception as e:
#         status = "failed"
#         raise HTTPException(
#             status_code=500,
#             detail=f'Задача по обработке с task_id: {task_id} завершилась неудачей. Ошибка: {str(e)}'
#         )
#     finally:
#         with Session(engine) as session:
#             statement = select(PredictImageJob).where(
#                 PredictImageJob.import_id == import_id,
#                 PredictImageJob.task_id == task_id
#             )
#             job = session.exec(statement).one()
#             job.status = status
#             job.updated_at = datetime.utcnow()
#             session.add(job)
#             session.commit()


# @dramatiq.actor
# def predict_cloud(
#     s3_our_bucket: str, 
#     import_id: str, 
#     task_id: str
# ):
#     """Функция распознания мусора на изображениях.

#     Получает изображения из s3://{s3_cloud_bucket}/{import_id}.
#     Результаты загружаются в s3://{s3_our_bucket}/{task_id}.
#     """
#     try:
#         with Session(engine) as session:
#             s3_credentials = session.exec(
#                 select(S3ClientData)
#                 .where(S3ClientData.id == import_id)
#             ).first()
#             if not s3_credentials:
#                 raise Exception(f'Сведений об: {s3_credentials} не найдено в БД.')
        
#         # Получаем словарь {URL : Метаданные} изображений на S3.
#         images_data = retrieve_images_urls_with_metadata(
#             s3_bucket=s3_credentials.bucket,
#             import_id=import_id,
#             from_cloud=True,
#             s3_cloud_data=s3_credentials
#         )
        
#         wrap_prediction(
#             model=model,
#             data=images_data,
#             s3_bucket=s3_our_bucket,
#             task_id=task_id
#         )
#     except Exception as e:
#         status = "failed"
#         raise HTTPException(
#             status_code=500,
#             detail=f'Задача по обработке с task_id: {task_id} завершилась неудачей. Ошибка: {str(e)}'
#         )
#     finally:
#         with Session(engine) as session:
#             statement = select(PredictImageJob).where(
#                 PredictImageJob.import_id == import_id,
#                 PredictImageJob.task_id == task_id
#             )
#             job = session.exec(statement).one()
#             job.status = status
#             job.updated_at = datetime.utcnow()
#             session.add(job)
#             session.commit()