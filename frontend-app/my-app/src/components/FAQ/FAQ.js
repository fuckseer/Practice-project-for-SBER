import React from "react";
import "./FAQ.css";

const FAQ = () => {
  const faqs = [
    { question: "Какие данные использовались для обучения модели?", answer: "8 терабайт данных c фотографиями моря были получены с камер GoPro при проведении экспедиции институтом проблем экологии и эволюции им. А.Н. Северцова. Камеры были установлены с двух сторон судна: Адекамик Мстислав Келдыш." },
    { question: "Где можно использовать эту систему?", answer: "в научных исследованиях, для экологического мониторинга, на кораблях." },
  ];

  return (
    <section id="faq" className="faq">
      <h2>FAQ</h2>
      {faqs.map((faq, index) => (
        <div key={index}>
          <p><strong>{faq.question}</strong></p>
          <p>{faq.answer}</p>
        </div>
      ))}
    </section>
  );
};

export default FAQ;
