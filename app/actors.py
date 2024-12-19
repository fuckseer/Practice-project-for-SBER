import os
import dramatiq

from s3 import bucket
from io import BytesIO
from model import model
from datetime import datetime
from PIL import Image, ExifTags
from sqlmodel import Session, select
from db_models import engine, ImportImageJob, S3ClientData
from predict import retrieve_images_urls_with_metadata, wrap_prediction


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
    #TODO: Сейчас работа с тасками из БД дает ошибки
    # поэтому весь каркас для работы с ImportImageJob выключен.
    
    # job = None # Иначе жалуется на отсутствие доступа к локальной job.
    # with Session(engine) as session:
    try:
        # query = select(ImportImageJob).where(
        #     ImportImageJob.import_id == import_id,
        #     ImportImageJob.image_filename == filename
        # )
        
        # job = session.exec(query).first()
        # if job:
        #     job.status = 'processing'
        #     job.updated_at = datetime.datetime.utcnow()
        #     session.add(job)
        #     session.commit()
        # else:
        #     raise Exception(f'Задачи для {filename} не найдено')

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
            
        # if job:
        #     job.status = 'completed'
        #     job.updated_at = datetime.datetime.utcnow()
        #     session.add(job)
        #     session.commit()

    except Exception as e:
        # if job:
        #     job.status = 'failed'
        #     job.updated_at = datetime.datetime.utcnow()
        #     session.add(job)
        #     session.commit()
        raise Exception(
            f"Ошибка загрузки файла: {filename}. Код ошибки: {str(e)}"
        )
    finally:
        #TODO: Раннее сохраненные пикчи нужно удалять,
        # сейчас при таком методе работы брокер несколько раз проставляет
        # задачу на одну и ту же пикчу, в результате для части задач, пикча
        # уже локально удалена и недоступна для обработки брокером, но он все 
        # равно продолжает пытаться обработать задачу. 
        # В целом, это работает (по-крайней мере локально), но выглядит максимально
        # убого.
        os.remove(filepath)


#TODO: Оба predict'а нужно обернуть с обращением к 
# инстансам тасок в базе данных (как в import_local),
# но чтоб работало...
@dramatiq.actor
def predict_local(
    s3_bucket: str, 
    import_id: str, 
    task_id: str
) -> None:
    """Функция распознания мусора на изображениях.

    Получает изображения из s3://{s3_bucket}/{import_id}.
    Результаты загружаются в s3://{s3_bucket}/{task_id}.
    """
    # Получаем словарь {URL : Метаданные} изображений на S3.
    images_data = retrieve_images_urls_with_metadata(
        import_id=import_id,
        s3_bucket=s3_bucket
    )
    
    wrap_prediction(
        model=model,
        data=images_data,
        s3_bucket=s3_bucket,
        task_id=task_id
    )


@dramatiq.actor
def predict_cloud(
    s3_our_bucket: str, 
    import_id: str, 
    task_id: str
):
    """Функция распознания мусора на изображениях.

    Получает изображения из s3://{s3_cloud_bucket}/{import_id}.
    Результаты загружаются в s3://{s3_our_bucket}/{task_id}.
    """
    with Session(engine) as session:
        s3_credentials = session.exec(
            select(S3ClientData)
            .where(S3ClientData.id == import_id)
        ).first()
        if not s3_credentials:
            raise Exception(f'Сведений об: {s3_credentials} не найдено в БД.')
    
    # Получаем словарь {URL : Метаданные} изображений на S3.
    images_data = retrieve_images_urls_with_metadata(
        s3_bucket=s3_credentials.bucket,
        import_id=import_id,
        from_cloud=True,
        s3_cloud_data=s3_credentials
    )
    
    wrap_prediction(
        model=model,
        data=images_data,
        s3_bucket=s3_our_bucket,
        task_id=task_id
    )
