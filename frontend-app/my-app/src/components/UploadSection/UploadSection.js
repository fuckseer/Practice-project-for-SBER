import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./UploadSection.css";

const UploadSection = () => {
  const [showModal, setShowModal] = useState(false); // Контроль модального окна
  const [cloudLink, setCloudLink] = useState(""); // Ссылка на облачное хранилище
  const [selectedFiles, setSelectedFiles] = useState([]); // Хранение выбранных файлов
  const [processedImages, setProcessedImages] = useState([]); // Список обработанных изображений
  const [csvLink, setCsvLink] = useState(null); // Ссылка на скачивание CSV-файла
  const [status, setStatus] = useState(null); // Статус загрузки
  const [loading, setLoading] = useState(false); // Для отображения процесса загрузки

  const fileInputRef = useRef(); // Ссылка на элемент input для файлов

  const handleCloudUpload = () => {
    if (!cloudLink) {
      alert("Введите ссылку на файл!");
      return;
    }

    // Эмуляция отправки ссылки и получения результата
    console.log("Отправка ссылки на бэкэнд:", cloudLink);
    setCloudLink(""); // Очистить поле после отправки
    setShowModal(false); // Закрыть модальное окно

    // Эмуляция ответа от бэкэнда
    setProcessedImages([
      "/path-to-processed-image1.jpg",
      "/path-to-processed-image2.jpg",
    ]); // Замените URL на реальные
    setCsvLink("/path-to-result.csv"); // Замените URL на реальный
    alert("Обработка завершена! Результаты доступны ниже.");
  };

  const handleFileUploadClick = () => {
    fileInputRef.current.click(); // Имитация нажатия на input для выбора файлов
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files); // Получение выбранных файлов
    setSelectedFiles(files);
    console.log("Выбраны файлы:", files.map((file) => file.name));
  };

  const handleFileUpload = () => {
    if (selectedFiles.length === 0) {
      alert("Выберите файлы для загрузки!");
      return;
    }

    // Создание объекта FormData для отправки файлов на сервер
    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("files", file));

    // Отправка файлов на сервер
    axios
      .post("YOUR_BACKEND_URL", formData, { headers: { "Content-Type": "multipart/form-data" } })
      .then((response) => {
        console.log("Файлы успешно загружены", response.data);
        setStatus(response.data.status); // Статус загрузки (in progress / complete)
        setLoading(true);
      })
      .catch((error) => {
        console.error("Ошибка при загрузке:", error);
        setLoading(false);
      });
  };

  // Функция для запроса статуса загрузки
  const checkStatus = () => {
    if (!status || status === "complete") return; // Проверяем статус загрузки

    // Проверяем статус загрузки на сервере
    axios
      .get("YOUR_STATUS_URL")
      .then((response) => {
        setStatus(response.data.status); // Обновляем статус

        if (response.data.status === "complete") {
          setProcessedImages([
            "/path-to-processed-image3.jpg", // Замените на реальные изображения
            "/path-to-processed-image4.jpg",
          ]);
          setCsvLink("/path-to-result.csv"); // Ссылка на скачивание CSV
        }
      })
      .catch((error) => {
        console.error("Ошибка при проверке статуса:", error);
      });
  };

  // Используем useEffect для периодического запроса статуса
  useEffect(() => {
    if (status === "in progress") {
      const interval = setInterval(() => {
        checkStatus();
      }, 5000); // Запрос статуса каждые 5 секунд

      return () => clearInterval(interval); // Очистка интервала при размонтировании компонента
    }
  }, [status]);

  const closeModal = (e) => {
    if (e.target.className === "modal") setShowModal(false);
  };

  return (
    <section className="upload-section">
      <p className="supported-formats">Поддерживаемые форматы: jpg, png</p>
      <div className="upload-options">
        <button
          className="orange-button"
          onClick={() => setShowModal(true)} // Открыть модальное окно
        >
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
          style={{ display: "none" }} // Скрытый input для файлов
          onChange={handleFileChange}
        />
      </div>

      {/* Отображение количества загруженных файлов */}
      {selectedFiles.length > 0 && (
        <p className="file-count">
          Выбрано файлов: {selectedFiles.length}
        </p>
      )}

      {/* Кнопка "Отправить", отображается только если выбраны файлы */}
      {selectedFiles.length > 0 && (
        <div className="file-upload-button">
          <button className="upload-button" onClick={handleFileUpload}>
            Отправить
          </button>
        </div>
      )}

      {/* Статус загрузки */}
      {loading && status === "in progress" && (
        <p className="status">Загрузка в процессе...</p>
      )}

      {/* Когда статус "complete", показываем ссылки на CSV и изображения */}
      {status === "complete" && (
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

      {/* Модальное окно для облачного хранилища */}
      {showModal && (
        <div className="modal" onClick={closeModal}>
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
