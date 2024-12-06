import os

import mlflow
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

DOWNLOAD_MODEL = os.getenv("DOWNLOAD_MODEL").lower() == "true"
MLFLOW_URL = os.getenv("MLFLOW_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_TAG = os.getenv("MODEL_TAG")
MODEL_PATH = f".models/{MODEL_TAG}"
MODEL_CONF = float(os.getenv("MODEL_CONF", "0.001"))

mlflow.set_tracking_uri(uri=MLFLOW_URL)


def get_model(download_model: bool):  # noqa: FBT001
    """Функция, которая загружает модель."""
    if download_model:
        print("The model is loading...")
        mlflow.artifacts.download_artifacts(
            f"models:/{MODEL_NAME}@{MODEL_TAG}", dst_path=MODEL_PATH
        )
        print("The model is loaded.")
    return YOLO(f"{MODEL_PATH}/best.pt")


model = get_model(DOWNLOAD_MODEL)
