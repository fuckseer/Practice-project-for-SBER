import os

import mlflow
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

DOWNLOAD_MODEL = os.environ["DOWNLOAD_MODEL"].lower() == "true"
MLFLOW_URL = os.getenv("MLFLOW_URL", "http://localhost:5000")
MODEL_NAME = os.getenv("MODEL_NAME", "coco")
MODEL_TAG = os.getenv("MODEL_TAG", "best")
MODEL_PATH = f".models/{MODEL_TAG}"

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
