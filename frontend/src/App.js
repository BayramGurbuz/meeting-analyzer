import React, { useEffect, useState } from "react";
import Recorder from "./Recorder";
import axios from "axios";
import "./App.css";

function App() {
  const [logs, setLogs] = useState([]);
  const [summary, setSummary] = useState("");

  useEffect(() => {
    // mount olurken eski logları temizle
    axios.post("http://127.0.0.1:8000/clear-logs").catch(console.error);

    // her saniye canlı logları çek
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

  const finishMeeting = async () => {
    try {
      // önce özet iste
      const { data: sumData } = await axios.get("http://127.0.0.1:8000/summarize");
      setSummary(sumData.summary);

      // sonra PDF raporu oluştur ve indir
      await axios.get("http://127.0.0.1:8000/generate-report");
      window.open("http://127.0.0.1:8000/download-report", "_blank");
    } catch (err) {
      console.error("Error ending meeting:", err);
      alert("Meeting summary or report failed.");
    }
  };

  return (
    <div className="app-container">
      {/* sol panel */}
      <div className="video-panel">
        <h1>Real-Time Meeting Analysis</h1>
        <br></br>
        <Recorder />

        <button className="btn-report" onClick={finishMeeting}>
          Summarize & Download Report
        </button>

        {summary && (
          <div className="summary-box">
            <h2>Meeting Summary</h2>
            <pre>{summary}</pre>
          </div>
        )}
      </div>

      {/* sağ panel */}
      <div className="transcript-panel">
        <h2>Live Transcripts & Emotions</h2>
        <div className="transcript-list">
          {logs.map((log, i) => (
            <div key={i} className="transcript-item">
              <div className="transcript-header">
                <span className="speaker-name">{log.speaker}</span>
                <span className="time-range">
                  [{log.start}s–{log.end}s]
                </span>
              </div>
              <div className="transcript-text">{log.text}</div>
              <div className="transcript-emotions">
                <span className="voice-tag">{log.voice_emotion}</span>
                <span className="visual-tag">{log.visual_emotion}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
