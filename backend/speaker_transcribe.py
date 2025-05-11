import whisper
import os
from diarization import diarize_audio, convert_to_wav
from emotion_analysis import analyze_emotion

model = whisper.load_model("medium")

def transcribe_segmented_speakers(webm_path):
    wav_path = webm_path.replace(".webm", ".wav")
    convert_to_wav(webm_path, wav_path)

    speaker_segments = diarize_audio(webm_path)
    transcription = model.transcribe(wav_path, language="en") 
    segments = transcription.get("segments", [])

    speaker_transcripts = []

    for speaker_segment in speaker_segments:
        s_start = speaker_segment["start"]
        s_end = speaker_segment["end"]
        speaker = speaker_segment["speaker"]

        matched_text = ""
        for seg in segments:
            seg_start = seg["start"]
            seg_end = seg["end"]

            if seg_end >= s_start and seg_start <= s_end:
                matched_text += seg["text"].strip() + " "

        speaker_transcripts.append({
            "speaker": speaker,
            "start": s_start,
            "end": s_end,
            "text": matched_text.strip(),
            "emotion":analyze_emotion(matched_text.strip())
        })

    return speaker_transcripts
