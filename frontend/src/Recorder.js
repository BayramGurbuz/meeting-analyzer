import React, { useRef, useState } from "react";
import axios from "axios";

const Recorder = () => {
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);
  const videoRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    streamRef.current = stream;

    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      videoRef.current.play();
    }

    const mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => {
      chunksRef.current.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunksRef.current, { type: "video/webm" });
      const formData = new FormData();
      formData.append("file", blob, "chunk.webm");

      await axios.post("http://localhost:8000/upload-chunk", formData);
      chunksRef.current = [];

      streamRef.current.getTracks().forEach((track) => track.stop());
      setIsRecording(false);
    };

    mediaRecorderRef.current = mediaRecorder;
    mediaRecorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }
  };

  return (
    <div>
      <h2>Meeting Record</h2>
      <video ref={videoRef} width="480" height="360" style={{ border: "1px solid #ccc" }} />
      <br />
      <button onClick={startRecording} disabled={isRecording}>
        Launch Camera and Send
      </button>
      <button onClick={stopRecording} disabled={!isRecording} style={{ marginLeft: "10px" }}>
        End Registration
      </button>
    </div>
  );
};
export default Recorder;
