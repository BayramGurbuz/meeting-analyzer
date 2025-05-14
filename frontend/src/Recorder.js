import React, { useRef, useState } from "react";
import axios from "axios";

const Recorder = () => {
  // sadece UI için: buton etiketini güncellemekte kullanacağız
  const [isRecording, setIsRecording] = useState(false);

  // gerçek kayıp durumu burada tutulacak
  const recordingRef = useRef(false);
  const streamRef = useRef(null);
  const recorderRef = useRef(null);
  const counterRef = useRef(0);

  // 1-chunk kaydını başlatıp 3s sonra durdurup, tekrar kendini çağıran fonksiyon
  const recordChunk = () => {
    if (!recordingRef.current || !streamRef.current) {
      console.log("recordChunk: kayıt modunda değil veya stream yok");
      return;
    }

    console.log("recordChunk: starting chunk", counterRef.current);

    const mediaRecorder = new MediaRecorder(streamRef.current, {
      mimeType: "video/webm",
    });
    recorderRef.current = mediaRecorder;

    mediaRecorder.onstart = () => {
      console.log("MediaRecorder started");
    };

    mediaRecorder.ondataavailable = async (e) => {
      console.log("ondataavailable, size:", e.data.size);
      if (e.data && e.data.size > 0) {
        const name = `chunk_${counterRef.current}.webm`;
        const form = new FormData();
        form.append("file", e.data, name);

        try {
          const resp = await axios.post(
            "http://127.0.0.1:8000/upload-chunk",
            form,
            { headers: { "Content-Type": "multipart/form-data" } }
          );
          console.log(name, "uploaded →", resp.data);
        } catch (err) {
          console.error("Upload error:", err);
        }

        counterRef.current += 1;
      }
    };

    mediaRecorder.onstop = () => {
      console.log("MediaRecorder stopped");
      // eğer hâlâ kayıttaysak, hemen bir sonraki parçayı başlat
      if (recordingRef.current) {
        recordChunk();
      }
    };

    // kayda başla ve 3s sonra stop et
    mediaRecorder.start();
    setTimeout(() => {
      if (mediaRecorder.state === "recording") {
        mediaRecorder.stop();
      }
    }, 3000);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      streamRef.current = stream;
      document.getElementById("preview").srcObject = stream;

      counterRef.current = 0;
      recordingRef.current = true;
      setIsRecording(true);

      console.log("startRecording: recordingRef set to true");
      recordChunk();
    } catch (err) {
      console.error("getUserMedia error:", err);
    }
  };

  const stopRecording = () => {
    console.log("stopRecording: recordingRef set to false");
    recordingRef.current = false;
    setIsRecording(false);

    // o anki recorder’ı durdur
    recorderRef.current?.stop();
    // kamerayı kapat
    streamRef.current?.getTracks().forEach((t) => t.stop());
  };

  return (
    <div>
      <h2>Real-time Meeting Recorder</h2>
      <video
        id="preview"
        width="400"
        height="300"
        autoPlay
        muted
        style={{ border: "1px solid #ccc" }}
      ></video>
      {!isRecording ? (
        <button onClick={startRecording}>Start Meeting</button>
      ) : (
        <button onClick={stopRecording}>Stop Meeting</button>
      )}
    </div>
  );
};

export default Recorder;
