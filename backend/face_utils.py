# backend/face_utils.py

import os
import numpy as np
from deepface import DeepFace
from scipy.spatial.distance import cosine

def load_known_faces(folder_path: str, model_name: str = "Facenet") -> dict:
    """
    Bilinen yüzleri yükler ve her biri için bir embedding (vektör) oluşturur.
    Çıktı: { "Ali": embedding_array, "Ayse": embedding_array, ... }
    """
    known = {}
    for fname in os.listdir(folder_path):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        name = os.path.splitext(fname)[0]
        img_path = os.path.join(folder_path, fname)
        # DeepFace.represent, enforce_detection=False ile yüz algılamaya takılmadan embedding döner
        rep = DeepFace.represent(img_path, model_name=model_name, enforce_detection=False)
        # represent bazen liste, bazen dict dönebilir
        if isinstance(rep, list) and isinstance(rep[0], dict):
            emb = np.array(rep[0]["embedding"])
        elif isinstance(rep, dict) and "embedding" in rep:
            emb = np.array(rep["embedding"])
        else:
            continue
        known[name] = emb
    return known

def match_face(image_path: str,
               known_faces: dict,
               threshold: float = 0.7,
               model_name: str = "Facenet") -> str | None:
    """
    Verilen karedeki yüz embedding'ini çıkarır ve en yakın bilinen yüzle karşılaştırır.
    Cosine distance < threshold ise eşleşme kabul edilir, aksi halde None döner.
    """
    try:
        rep = DeepFace.represent(image_path, model_name=model_name, enforce_detection=False)
    except Exception:
        return None

    if isinstance(rep, list) and isinstance(rep[0], dict):
        query_emb = np.array(rep[0]["embedding"])
    elif isinstance(rep, dict) and "embedding" in rep:
        query_emb = np.array(rep["embedding"])
    else:
        return None

    best_match = None
    lowest_dist = 1.0
    # En küçük cosine mesafesini bulan kişi
    for name, emb in known_faces.items():
        dist = cosine(query_emb, emb)
        if dist < lowest_dist:
            lowest_dist = dist
            best_match = name

    if lowest_dist <= threshold:
        return best_match
    return None
