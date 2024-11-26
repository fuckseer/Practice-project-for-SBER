# Импорты
import mlflow
from ultralytics import YOLO, settings

# Константы
DATA = "coco8.yaml"
EPOCHS = 3
TEST_IMAGE = "000000000113.jpg"
MLFLOW_URI = "http://waste.sergei-kiprin.ru:5000"
EXPERIMENT = "coco8"

# Настройки MLFlow
mlflow.set_tracking_uri(uri=MLFLOW_URI)
mlflow.set_experiment(EXPERIMENT)

# Включаем автоматическое логирование MLFlow для YOLO
settings.update({"mlflow": True})

# Начинаем новый Run
with mlflow.start_run() as run:

    # Трекаем параметры
    mlflow.log_param("epochs_count", EPOCHS)
    mlflow.log_param("test_image", TEST_IMAGE)

    # Добавляем теги
    mlflow.set_tag("Project", "COCO Detection")

    # Тренируем, валидируем модель (YOLO автоматически сохранит парметры, метрики, артефакты)
    model = YOLO("yolo11n.pt")
    model.train(data=DATA, epochs=EPOCHS)
    model.val()
    model.export()

    # Тестируем модель
    test_results = model.predict(TEST_IMAGE)
    # Сохраняем метрику и тестируемую картинку
    mlflow.log_metric('metrics/test_image_detections_count', len(test_results[0].boxes))
    mlflow.log_artifact(TEST_IMAGE)

    # Сохраняем модель PyTorch
    mlflow.pytorch.log_model(model.model, artifact_path="weights")
