import os
from diarization import diarize_audio, convert_to_wav
from emotion_analysis import analyze_emotion
from frame_extractor import extract_frames
from deepface import DeepFace
import whisper

def get_frame_second(filename):
    return int(filename.split("_")[1].split(".")[0])

def find_visual_emotion_for_segment(start, end, frame_emotions):
    relevant = [f["emotion"] for f in frame_emotions if start <= f["second"] <= end and f["emotion"] != "error"]
    if not relevant:
        return "unknown"
    return max(set(relevant), key=relevant.count)

def speaker_multimodal_analysis(video_path):
    wav_path = video_path.replace(".webm", ".wav")
    convert_to_wav(video_path, wav_path)

    speaker_segments = diarize_audio(video_path)

    model = whisper.load_model("base")
    transcription = model.transcribe(wav_path, language="en")
    segments = transcription.get("segments", [])

    extract_frames(video_path, fps=1)
    frame_emotions = []
    for file in sorted(os.listdir("frames")):
        if not file.endswith(".jpg"):
            continue
        second = get_frame_second(file)
        file_path = os.path.join("frames", file)
        try:
            analysis = DeepFace.analyze(img_path=file_path, actions=['emotion'], enforce_detection=False)
            emotion = analysis[0]['dominant_emotion']
        except Exception:
            emotion = "error"
        frame_emotions.append({"second": second, "emotion": emotion})

    results = []
    for segment in speaker_segments:
        s_start = segment["start"]
        s_end = segment["end"]
        speaker = segment["speaker"]

        matched_text = ""
        for seg in segments:
            if seg["end"] >= s_start and seg["start"] <= s_end:
                matched_text += seg["text"].strip() + " "

        matched_text = matched_text.strip()
        voice_emotion = analyze_emotion(matched_text)
        visual_emotion = find_visual_emotion_for_segment(s_start, s_end, frame_emotions)

        results.append({
            "speaker": speaker,
            "start": s_start,
            "end": s_end,
            "text": matched_text,
            "voice_emotion": voice_emotion,
            "visual_emotion": visual_emotion
        })

    return results
