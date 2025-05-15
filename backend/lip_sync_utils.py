# backend/lip_sync_utils.py

import cv2
import numpy as np
import mediapipe as mp

# Mediapipe FaceMesh ayarları
mp_face_mesh = mp.solutions.face_mesh
# Ağız dolgusunu gösteren landmark indeksleri
# (üst-lip, alt-lip, sol köşe, sağ köşe)
MOUTH_IDX = {
    "upper": 13,    # üst ortadaki noktaya karşılık
    "lower": 14,    # alt ortadaki noktaya karşılık
    "left": 61,     # sol köşe
    "right": 291    # sağ köşe
}

def compute_mar(image_path: str) -> float | None:
    """
    Verilen karedeki (frame) yüzün mouth aspect ratio'sunu (MAR) döner.
    MAR = (alt–üst mesafe) / (köşe arası mesafe)
    Eğer yüz bulunamazsa None döner.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5
    ) as face_mesh:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = face_mesh.process(rgb)
        if not res.multi_face_landmarks:
            return None

        lm = res.multi_face_landmarks[0].landmark
        h, w, _ = img.shape

        def xy(idx):
            pt = lm[idx]
            return np.array([pt.x * w, pt.y * h])

        upper = xy(MOUTH_IDX["upper"])
        lower = xy(MOUTH_IDX["lower"])
        left  = xy(MOUTH_IDX["left"])
        right = xy(MOUTH_IDX["right"])

        vertical = np.linalg.norm(lower - upper)
        horizontal = np.linalg.norm(right - left)
        if horizontal == 0:
            return None
        return float(vertical / horizontal)
