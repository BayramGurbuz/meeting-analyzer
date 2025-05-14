# backend/test_face_utils.py

"""
Basit bir test script’i:
– ‘known_faces/’ klasöründeki yüzleri yükler
– Komut satırından verilen görseldeki yüzle eşleşip eşleşmediğini kontrol eder

Kullanım:
  cd backend
  python test_face_utils.py path/to/test_image.jpg
"""

import sys
import os

from face_utils import load_known_faces, match_face

def main():
    # 1) Bilinen yüzleri yükle
    known_folder = "known_faces"
    if not os.path.isdir(known_folder):
        print(f"Hata: '{known_folder}' klasörü bulunamadı.")
        sys.exit(1)

    known_faces = load_known_faces(known_folder)
    if not known_faces:
        print(f"Hata: '{known_folder}' içinde yüklenebilecek yüz resmi yok.")
        sys.exit(1)

    print("Yüklenen bilinen yüzler:", list(known_faces.keys()))

    # 2) Test edilecek görsel yolu
    if len(sys.argv) < 2:
        print("Kullanım: python test_face_utils.py <test_image_path>")
        sys.exit(1)

    test_image = sys.argv[1]
    if not os.path.isfile(test_image):
        print(f"Hata: '{test_image}' dosyası bulunamadı.")
        sys.exit(1)

    # 3) Eşleştirme
    match = match_face(test_image, known_faces)
    if match:
        print(f"Eşleşen yüz: {match}")
    else:
        print("Hiçbir bilinen yüzle eşleşme bulunamadı.")

if __name__ == "__main__":
    main()
