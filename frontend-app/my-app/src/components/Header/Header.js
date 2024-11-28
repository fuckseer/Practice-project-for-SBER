import React from 'react';
import './Header.css';

function Header() {
  return (
    <header
      className="header">
      <nav className="navbar">
        <ul className="nav-links">
          <li>
            <a href="#examples">примеры изображений</a>
          </li>
          <li>
            <a href="#faq">FAQ</a>
          </li>
        </ul>
      </nav>
      <h1>ДЕТЕКЦИЯ МОРСКОГО МУСОРА</h1>
      <p>Модель искусственного интеллекта YOLOv10 для распознавания морского мусора на большом количестве фотографий</p>
    </header>
  );
}

export default Header;
;


