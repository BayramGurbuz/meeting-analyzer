// frontend/src/App.js

import React, { useEffect, useState } from "react";
import Recorder from "./Recorder";
import axios from "axios";

function App() {
  const [logs, setLogs] = useState([]);

  // Sayfa yüklendiğinde ve toplantı başlarken logları temizle ve ardından live-logs’ları her saniye çek
  useEffect(() => {
    // 1) Backend live_logs listesini temizle
    axios
      .post("http://127.0.0.1:8000/clear-logs")
      .then(() => console.log("Live logs cleared on mount"))
      .catch((err) => console.error("Error clearing live logs:", err));

    // 2) Her saniye live-logs endpoint’ini çağır
    const interval = setInterval(async () => {
      try {
        const { data } = await axios.get("http://127.0.0.1:8000/live-logs");
        setLogs(data.logs);
      } catch (err) {
        console.error("Live logs fetch error:", err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Toplantıyı durdur ve özet raporu oluştur
  const finishMeeting = async () => {
    try {
      await axios.get("http://127.0.0.1:8000/generate-report");
      window.open("http://127.0.0.1:8000/download-report", "_blank");
    } catch (err) {
      console.error("Report generation error:", err);
      alert("Rapor oluşturulamadı.");
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Real-time Meeting Analysis</h1>
      <Recorder />
      <button onClick={finishMeeting} style={{ marginTop: 20 }}>
        Stop & Generate Summary
      </button>
      <div style={{ marginTop: 30 }}>
        <h2>Live Transcripts & Emotions</h2>
        {logs.map((log, i) => (
          <div key={i} style={{ marginBottom: 10 }}>
            {/* start and end zamanlarını panelde göster */}
            <strong>{log.speaker}</strong> [{log.start}s–{log.end}s]:{" "}
            {log.text}{" "}
            <em>({log.voice_emotion} / {log.visual_emotion})</em>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
