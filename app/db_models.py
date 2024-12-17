from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field

# Модель для Request Body запроса импорта с S3.
class S3Request(BaseModel):
    s3_path_to_folder: str
    endpoint_url: str
    access_key : str
    secret_key : str


# Модель таблицы для данных S3.
class S3Credentials(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    s3_path_to_folder: str
    endpoint_url: str
    access_key: str
    secret_key: str
