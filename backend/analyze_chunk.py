# backend/analyze_chunk.py

import os
import whisper
from deepface import DeepFace
from diarization import convert_to_wav, diarize_audio
from emotion_analysis import analyze_emotion
from frame_extractor import extract_frames
from face_utils import load_known_faces, match_face
from pydub import AudioSegment

# 1) Bilinen yüzleri ön yükle
KNOWN_FACES_FOLDER = "known_faces"
known_faces = load_known_faces(KNOWN_FACES_FOLDER)
print(f"[DEBUG] Loaded known faces: {list(known_faces.keys())}")

# 2) Whisper modelini yükle
whisper_model = whisper.load_model("base")


def analyze_chunk(chunk_path: str) -> list[dict]:
    """
    .webm video parçası alır, speaker-diarization,
    segment-by-segment transcribe + emotion + face-ID uygulayıp
    bir liste döner:
    [
      {
        "speaker": "BayG",
        "start": 0.00, "end": 2.34,
        "text": "...",
        "voice_emotion": "...",
        "visual_emotion": "..."
      },
      ...
    ]
    """

    # A) .webm → .wav
    wav_path = chunk_path.replace(".webm", ".wav")
    convert_to_wav(chunk_path, wav_path)

    # B) Diarize: [{'speaker':'SPEAKER_00','start':x,'end':y},...]
    segments = diarize_audio(wav_path)
    print(f"[DEBUG] Diarized segments: {segments}")

    # C) Load full audio with pydub
    audio = AudioSegment.from_file(wav_path)

    # D) Extract all frames once
    extract_frames(chunk_path, fps=2)
    all_frames = sorted(os.listdir("frames"))

    results = []

    for seg in segments:
        s, e = seg["start"], seg["end"]
        speaker_id = seg["speaker"]

        # 1) Transcribe only this slice
        start_ms, end_ms = int(s * 1000), int(e * 1000)
        snippet = audio[start_ms:end_ms]
        temp_wav = f"temp_{start_ms}_{end_ms}.wav"
        snippet.export(temp_wav, format="wav")

        transcript = whisper_model.transcribe(temp_wav, language="en")
        text = transcript.get("text", "").strip()
        os.remove(temp_wav)

        # 2) Voice emotion
        voice_emotion = analyze_emotion(text)

        # 3) Face-ID & visual emotion: only frames in [s,e]
        segment_frames = []
        for f in all_frames:
            sec = int(f.split("_")[1].split(".")[0])
            if s <= sec <= e:
                segment_frames.append(f)

        names = []
        for f in segment_frames:
            name = match_face(os.path.join("frames", f), known_faces)
            if name:
                names.append(name)
        speaker_name = max(set(names), key=names.count) if names else "Unknown"

        # visual emotion on last frame if exists
        visual_emotion = "unknown"
        if segment_frames and speaker_name != "Unknown":
            last = segment_frames[-1]
            analysis = DeepFace.analyze(
                img_path=os.path.join("frames", last),
                actions=["emotion"],
                enforce_detection=False
            )
            if isinstance(analysis, list) and analysis:
                analysis = analysis[0]
            visual_emotion = analysis.get("dominant_emotion", "unknown")

        results.append({
            "speaker": speaker_name,
            "start": round(s, 2),
            "end": round(e, 2),
            "text": text,
            "voice_emotion": voice_emotion,
            "visual_emotion": visual_emotion
        })

    return results
