import React from "react";
import "./Examples.css";

// Импортируем изображения, так как они находятся внутри `src`
import image1 from "./1.jpg";
import image2 from "./2.jpg";
import image3 from "./3.jpg";
import image4 from "./4.jpg";
import image5 from "./5.jpg";

const Examples = () => {
  const exampleImages = [
    image1, // Импортированные пути к изображениям
    image2,
    image3,
    image4,
    image5,
  ];

  return (
    <section id="examples" className="examples">
      <h2>ПРИМЕРЫ ИЗОБРАЖЕНИЙ</h2>
      <div className="image-grid">
        {exampleImages.map((image, index) => (
          <img key={index} src={image} alt={`Пример ${index + 1}`} />
        ))}
      </div>
    </section>
  );
};

export default Examples;


