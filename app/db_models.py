import os

from typing import Optional
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field, Session, create_engine


load_dotenv()

DB_CONNECTION_STRING = os.getenv("POSTGRESQL_CONNECTION_STRING", 'sqlite:///waste.db')
engine = create_engine(DB_CONNECTION_STRING)


def get_session():
    """DI для DB сессии"""
    with Session(engine) as session:
        yield session


# Модель для Request Body запроса импорта с S3.
class S3Request(BaseModel):
    s3_path_to_folder: str
    access_key : str
    secret_key : str


# Модель таблицы для данных S3.
class S3ClientData(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    full_path : str
    subdirectories_path : str
    folder: str
    bucket: str
    endpoint_url: str
    access_key: str
    secret_key: str


#TODO: Сделать еще одну модель для отслеживания статусов
# распознаний пикч.

# Модель таблицы для отслеживания статусов импорта.
class ImportImageJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    import_id: str = Field(index=True)
    image_filename: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
