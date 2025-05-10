import subprocess
import os
from pyannote.audio import Pipeline

HUGGINGFACE_TOKEN = "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"  # Tokenı buraya yaz
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token=HUGGINGFACE_TOKEN
)

def convert_to_wav(input_path, output_path=None):
    if output_path is None:
        output_path = input_path.replace(".webm", ".wav")
    command = ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", output_path]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def diarize_audio(audio_path):
    wav_path = audio_path.replace(".webm", ".wav")
    convert_to_wav(audio_path, wav_path)
    diarization = pipeline(wav_path)
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": round(turn.start, 2),
            "end": round(turn.end, 2),
            "speaker": speaker
        })
    return segments