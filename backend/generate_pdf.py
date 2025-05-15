# backend/generate_pdf.py

import json
from collections import Counter
from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile

def safe_text(text: str) -> str:
    # PDF’in Latin-1 kodlamasına uymayan karakterleri yedek silin
    return text.encode("latin-1", "replace").decode("latin-1")

def draw_bar_chart(counter_data: Counter, title: str) -> BytesIO:
    fig, ax = plt.subplots()
    ax.bar(counter_data.keys(), counter_data.values(), color='skyblue')
    ax.set_title(title)
    ax.set_ylabel("Count")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_pdf(report_data: dict, output_path: str = "advanced_speech_report.pdf"):
    """
    report_data: {
      "results": [ {speaker,start,end,text,voice_emotion,visual_emotion}, ... ],
      "summary": "Madde madde özet metni\n..."
    }
    """
    results = report_data.get("results", [])
    summary = report_data.get("summary", "")

    # Konuşmacıya göre grupla
    speeches_by_speaker: dict[str, list] = {}
    for entry in results:
        sp = entry["speaker"]
        speeches_by_speaker.setdefault(sp, []).append(entry)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Başlık sayfası
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, safe_text("Meeting Analysis Report"), ln=True, align='C')
    pdf.ln(10)

    # ➊ Özet Bölümü
    if summary:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, safe_text("Meeting Summary:"), ln=True)
        pdf.ln(2)
        pdf.set_font("Arial", size=12)
        for line in summary.split("\n"):
            pdf.multi_cell(0, 8, safe_text(line))
        pdf.add_page()

    # ➋ Her Konuşmacı İçin Detaylar
    for speaker, speeches in speeches_by_speaker.items():
        durations = [s["end"] - s["start"] for s in speeches]

        # artık voice_emotion string veya dict olabilir
        voice_emotions = []
        for s in speeches:
            ve = s.get("voice_emotion")
            if isinstance(ve, dict):
                voice_emotions.append(ve.get("label", "unknown"))
            else:
                voice_emotions.append(str(ve or "unknown"))

        visual_emotions = []
        for s in speeches:
            ve = s.get("visual_emotion")
            if isinstance(ve, dict):
                visual_emotions.append(ve.get("label", "unknown"))
            else:
                visual_emotions.append(str(ve or "unknown"))

        emotion_transitions = " → ".join(voice_emotions)
        avg_dur = sum(durations) / len(durations) if durations else 0
        min_dur = min(durations) if durations else 0
        max_dur = max(durations) if durations else 0

        voice_counts = Counter(voice_emotions)
        visual_counts = Counter(visual_emotions)

        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, safe_text(f"Speaker: {speaker}"), ln=True)
        pdf.set_font("Arial", 'I', 12)
        pdf.cell(0, 8, safe_text(f"Total Speech Count: {len(speeches)}"), ln=True)
        pdf.cell(0, 8, safe_text(f"Total Duration: {sum(durations):.2f}s"), ln=True)
        pdf.cell(0, 8, safe_text(f"Average Duration: {avg_dur:.2f}s"), ln=True)
        pdf.cell(0, 8, safe_text(f"Shortest Speech: {min_dur:.2f}s"), ln=True)
        pdf.cell(0, 8, safe_text(f"Longest Speech: {max_dur:.2f}s"), ln=True)
        pdf.multi_cell(0, 8, safe_text(f"Emotion Transitions: {emotion_transitions}"))
        pdf.ln(4)

        # Dağılımlar
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, safe_text("Voice Emotion Distribution:"), ln=True)
        pdf.set_font("Arial", size=12)
        for emo, cnt in voice_counts.items():
            pct = cnt / len(voice_emotions) * 100 if voice_emotions else 0
            pdf.cell(0, 8, safe_text(f"  - {emo}: {cnt} ({pct:.1f}%)"), ln=True)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, safe_text("Visual Emotion Distribution:"), ln=True)
        pdf.set_font("Arial", size=12)
        for emo, cnt in visual_counts.items():
            pct = cnt / len(visual_emotions) * 100 if visual_emotions else 0
            pdf.cell(0, 8, safe_text(f"  - {emo}: {cnt} ({pct:.1f}%)"), ln=True)
        pdf.ln(4)

        # Grafik
        buf = draw_bar_chart(voice_counts, f"{speaker} - Voice Emotions")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpf:
            tmpf.write(buf.read())
            tmpf.flush()
            pdf.image(tmpf.name, x=10, w=100)
        buf.close()
        pdf.ln(10)

        # Detaylı Konuşma Metni
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, safe_text("Speech Details:"), ln=True)
        pdf.set_font("Arial", size=12)
        for i, sp in enumerate(speeches, 1):
            t = sp["text"].strip() or "[No text]"
            ve_label = sp.get("voice_emotion")
            if isinstance(ve_label, dict):
                ve_label = ve_label.get("label", "")
            ve_label = ve_label if isinstance(ve_label, str) else str(ve_label)

            vi_label = sp.get("visual_emotion")
            if isinstance(vi_label, dict):
                vi_label = vi_label.get("label", "")
            vi_label = vi_label if isinstance(vi_label, str) else str(vi_label)

            pdf.multi_cell(0, 8, safe_text(f"{i}. [{sp['start']:.2f}-{sp['end']:.2f}] {t}"))
            pdf.multi_cell(0, 8, safe_text(f"   Voice: {ve_label}"))
            pdf.multi_cell(0, 8, safe_text(f"   Visual: {vi_label}"))
            pdf.ln(3)

        pdf.add_page()

    # Son olarak kaydet
    pdf.output(output_path)
    print(f"PDF successfully created: {output_path}")
