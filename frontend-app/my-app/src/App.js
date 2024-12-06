import React from "react";
import Header from "./components/Header/Header";
import UploadSection from "./components/UploadSection/UploadSection";
import Examples from "./components/Examples/Examples";
import FAQ from "./components/FAQ/FAQ";
import "./App.css";

function App() {
  return (
    <div className="App">
      <div className="page-background">
        <Header />
        <UploadSection />
        <Examples />
      </div>
      <FAQ />
    </div>
  );
}

export default App;

