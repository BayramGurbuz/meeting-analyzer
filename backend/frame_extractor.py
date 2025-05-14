# backend/frame_extractor.py

import os
import shutil
import subprocess

def extract_frames(video_path: str, fps: int = 1):
    """
    Verilen video dosyasından FFmpeg ile kareleri kesip 'frames/' klasörüne kaydeder.
    - video_path: .webm gibi bir video dosyası
    - fps: saniyede kaç kare alınacağı (ör. fps=1 ise her saniyede 1 kare)
    """

    frames_dir = "frames"

    # 1) Mevcut frames klasörünü sil + yeniden oluştur
    if os.path.exists(frames_dir):
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir, exist_ok=True)

    # 2) FFmpeg komutunu hazırla ve çalıştır
    #    -y: var olan dosyaları üzerine yazar
    #    -i: giriş dosyası
    #    -vf fps=... : saniyede kaç kare üretileceği
    #    frames/frame_%03d.jpg : çıktı formatı
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"fps={fps}",
        os.path.join(frames_dir, "frame_%03d.jpg")
    ]
    # sessizce çalıştırıyoruz
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3) Basit bir debug için kaç kare oluştuğunu yazdırmak isteyebilirsiniz:
    print(f"[DEBUG] Frames in '{frames_dir}':", os.listdir(frames_dir))
