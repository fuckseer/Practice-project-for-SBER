import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./UploadSection.css";

const UploadSection = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [cloudLink, setCloudLink] = useState("");
  const [importId, setImportId] = useState(null);
  const [taskId, setTaskId] = useState(null);
  const [statusMessage, setStatusMessage] = useState(null);
  const [processedImages, setProcessedImages] = useState([]);
  const [csvLink, setCsvLink] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const fileInputRef = useRef();

  // Загрузка файлов с устройства
  const handleFileUploadClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);
    console.log("Выбраны файлы:", files.map((file) => file.name));
  };

  const handleFileUpload = () => {
    if (selectedFiles.length === 0) {
      alert("Выберите файлы для загрузки!");
      return;
    }

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("images", file));

    setStatusMessage("Загрузка файлов...");

    axios
      .post("http://localhost:7860/api/import/local", formData)
      .then((response) => {
        const { import_id } = response.data;
        console.log("Импорт завершён, import_id:", import_id);
        setImportId(import_id);
        setStatusMessage("Файлы загружены. Начинается обработка...");
        checkImportStatus(import_id);
      })
      .catch((error) => {
        console.error("Ошибка при загрузке файлов:", error);
        setStatusMessage("Ошибка загрузки файлов.");
      });
  };

  // Проверка статуса импорта
  const checkImportStatus = (importId) => {
    const interval = setInterval(() => {
      axios
        .get(`http://localhost:7860/api/import/status/${importId}`)
        .then((response) => {
          if (response.data.status === "ready") {
            clearInterval(interval);
            startPrediction(importId);
          }
        })
        .catch((error) => {
          console.error("Ошибка при проверке статуса импорта:", error);
        });
    }, 3000);
  };

  // Запуск предсказания
  const startPrediction = (importId) => {
    setStatusMessage("Обработка изображений...");

    axios
      .post(`http://localhost:7860/api/predict/${importId}`)
      .then((response) => {
        const { task_id } = response.data;
        console.log("Начато предсказание, task_id:", task_id);
        setTaskId(task_id);
        checkPredictionStatus(task_id);
      })
      .catch((error) => {
        console.error("Ошибка при запуске предсказания:", error);
        setStatusMessage("Ошибка обработки изображений.");
      });
  };

  // Проверка статуса предсказания
  const checkPredictionStatus = (taskId) => {
    const interval = setInterval(() => {
      axios
        .get(`http://localhost:7860/api/predict/status/${taskId}`)
        .then((response) => {
          if (response.data.status === "ready") {
            clearInterval(interval);
            fetchResults(taskId);
          }
        })
        .catch((error) => {
          console.error("Ошибка при проверке статуса предсказания:", error);
        });
    }, 3000);
  };

  // Получение результатов
  const fetchResults = (taskId) => {
    axios
      .get(`http://localhost:7860/api/results/${taskId}`)
      .then((response) => {
        const { csv, images } = response.data;
        console.log("Результаты получены:", csv, images);
        setCsvLink(csv);
        setProcessedImages(images);
        setStatusMessage("Обработка завершена!");
      })
      .catch((error) => {
        console.error("Ошибка при получении результатов:", error);
        setStatusMessage("Ошибка получения результатов.");
      });
  };

  // Эмуляция обработки загрузки из облака
  const handleCloudUpload = () => {
    if (!cloudLink) {
      alert("Введите ссылку на файл!");
      return;
    }

    setStatusMessage("Загрузка файлов из облачного хранилища...");
    setCloudLink("");
    setShowModal(false);

    // Эмуляция завершения процесса
    setTimeout(() => {
      setProcessedImages([
        "/path-to-processed-image1.jpg",
        "/path-to-processed-image2.jpg",
      ]);
      setCsvLink("/path-to-result.csv");
      setStatusMessage("Обработка завершена! Результаты доступны ниже.");
    }, 3000);
  };

  return (
    <section className="upload-section">
      <p className="supported-formats">Поддерживаемые форматы: jpg, png</p>
      <div className="upload-options">
        <button className="orange-button" onClick={() => setShowModal(true)}>
          <span className="main-text">Загрузить</span>
          <br />
          <span className="sub-text">из облачного хранилища</span>
        </button>
        <span className="or-text">или</span>
        <button className="blue-button" onClick={handleFileUploadClick}>
          <span className="main-text">Загрузить</span>
          <br />
          <span className="sub-text">с устройства</span>
        </button>
        <input
          type="file"
          ref={fileInputRef}
          accept=".jpg,.png"
          multiple
          style={{ display: "none" }}
          onChange={handleFileChange}
        />
      </div>

            {/* Отображение количества загруженных файлов */}
      {selectedFiles.length > 0 && (
        <p className="file-count">
          Выбрано файлов: {selectedFiles.length}
        </p>
      )}

      {selectedFiles.length > 0 && (
        <div className="file-upload-button">
          <button className="upload-button" onClick={handleFileUpload}>
            Запустить предсказание
          </button>
        </div>
      )}

      {statusMessage && <p className="status">{statusMessage}</p>}

      {csvLink && (
        <div className="download-section">
          <a href={csvLink} download className="csv-download-button">
            Скачать результат (CSV)
          </a>
          <div className="processed-images">
            <h3>Обработанные изображения:</h3>
            <div className="image-grid">
              {processedImages.map((image, index) => (
                <img
                  key={index}
                  src={image}
                  alt={`Обработанное изображение ${index + 1}`}
                  className="processed-image"
                />
              ))}
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div className="modal" onClick={(e) => e.target.className === "modal" && setShowModal(false)}>
          <div className="modal-content">
            <h2>Введите ссылку на S3-хранилище</h2>
            <input
              type="text"
              placeholder="https://example.com/your-file"
              value={cloudLink}
              onChange={(e) => setCloudLink(e.target.value)}
              className="cloud-link-input"
            />
            <button className="upload-button" onClick={handleCloudUpload}>
              Отправить
            </button>
          </div>
        </div>
      )}
    </section>
  );
};

export default UploadSection;
