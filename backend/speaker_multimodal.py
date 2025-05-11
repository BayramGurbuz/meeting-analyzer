import os
from diarization import diarize_audio, convert_to_wav
from emotion_analysis import analyze_emotion
from frame_extractor import extract_frames
from deepface import DeepFace
import whisper

def get_frame_second(filename):
    return int(filename.split("_")[1].split(".")[0])

def find_visual_emotion_for_segment(start, end, frame_emotions):
    relevant = [f for f in frame_emotions if start <= f["second"] <= end and f["emotion"] != "error"]
    if not relevant:
        return {"label": "unknown", "confidence": 0.0}
    emotions = [f["emotion"] for f in relevant]
    dominant = max(set(emotions), key=emotions.count)
    confidence = emotions.count(dominant) / len(emotions)
    return {"label": dominant, "confidence": round(confidence, 2)}

def speaker_multimodal_analysis(video_path):
    wav_path = video_path.replace(".webm", ".wav")
    convert_to_wav(video_path, wav_path)
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"{wav_path} not found after conversion.")

    speaker_segments = diarize_audio(wav_path)
    speaker_segments = [s for s in speaker_segments if s["end"] - s["start"] >= 0.5]  # kısa segmentleri filtrele

    model = whisper.load_model("large")
    transcription = model.transcribe(wav_path, language="en")
    segments = transcription.get("segments", [])

    extract_frames(video_path, fps=8)
    frame_emotions = []
    for file in sorted(os.listdir("frames")):
        if not file.endswith(".jpg"):
            continue
        second = get_frame_second(file)
        file_path = os.path.join("frames", file)
        try:
            analysis = DeepFace.analyze(img_path=file_path, actions=['emotion'], enforce_detection=True)
            emotion = analysis[0]['dominant_emotion']
            confidence = round(analysis[0]['emotion'][emotion], 2)
        except Exception:
            emotion = "error"
            confidence = 0.0
        frame_emotions.append({"second": second, "emotion": emotion, "confidence": confidence})

    results = []
    used_segments = set()
    for segment in speaker_segments:
        s_start = segment["start"]
        s_end = segment["end"]
        speaker = segment["speaker"]

        matched_text = ""
        for seg in segments:
            seg_id = (seg["start"], seg["end"])
            if seg_id in used_segments:
                continue
            if seg["end"] >= s_start and seg["start"] <= s_end:
                matched_text += seg["text"].strip() + " "
                used_segments.add(seg_id)

        matched_text = matched_text.strip()
        if not matched_text:
            continue

        voice_emotion_label = analyze_emotion(matched_text)
        visual_emotion = find_visual_emotion_for_segment(s_start, s_end, frame_emotions)

        results.append({
            "speaker": speaker,
            "start": s_start,
            "end": s_end,
            "text": matched_text,
            "voice_emotion": {"label": voice_emotion_label, "confidence": 1.0},
            "visual_emotion": visual_emotion
        })

    return results
