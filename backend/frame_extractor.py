import os
import subprocess

def extract_frames(video_path, output_folder="frames", fps=8):
    os.makedirs(output_folder, exist_ok=True)
    command = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps={fps}",
        f"{output_folder}/frame_%03d.jpg"
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)