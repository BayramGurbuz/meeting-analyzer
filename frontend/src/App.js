import React from "react";
import Recorder from "./Recorder";

function App() {
  return (
    <div className="App">
      <h1>Toplantı Analiz Sistemi</h1>
      <Recorder />

      {/* PDF İndirme Butonu */}
      <div style={{ marginTop: "20px" }}>
        <a
          href="http://localhost:8000/download-report"
          target="_blank"
          rel="noopener noreferrer"
          download
        >
          <button>PDF Raporu İndir</button>
        </a>
      </div>
    </div>
  );
}

export default App;
