import json
from collections import Counter
from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile
from speaker_multimodal import speaker_multimodal_analysis

def safe_text(text):
    return text.encode("latin-1", "replace").decode("latin-1")

# 1. Perform the analysis and create the JSON file
video_path = "uploaded_chunks/chunk.webm"
data = speaker_multimodal_analysis(video_path)
with open("multimodal_output.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# 2. Generate PDF report from JSON
speeches_by_speaker = {}
for entry in data:
    speaker = entry["speaker"]
    if speaker not in speeches_by_speaker:
        speeches_by_speaker[speaker] = []
    speeches_by_speaker[speaker].append(entry)

# PDF class
def draw_bar_chart(counter_data, title):
    fig, ax = plt.subplots()
    ax.bar(counter_data.keys(), counter_data.values(), color='skyblue')
    ax.set_title(title)
    ax.set_ylabel("Count")
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, safe_text("Speech Analysis Report"), ln=True, align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

# Analysis and details for each speaker
total_duration = 0
for speaker, speeches in speeches_by_speaker.items():
    durations = [s["end"] - s["start"] for s in speeches]
    voice_emotions = [s["voice_emotion"]["label"] for s in speeches]
    visual_emotions = [s["visual_emotion"]["label"] for s in speeches]

    emotion_transitions = " → ".join(voice_emotions)
    avg_duration = sum(durations) / len(durations)
    min_duration = min(durations)
    max_duration = max(durations)
    total_duration += sum(durations)

    voice_counts = Counter(voice_emotions)
    visual_counts = Counter(visual_emotions)

    pdf.set_font("Arial", 'B', 13)
    pdf.cell(0, 10, safe_text(f"Speaker: {speaker}"), ln=True)
    pdf.set_font("Arial", 'I', 12)
    pdf.cell(0, 8, safe_text(f"Total Speech Count: {len(speeches)}"), ln=True)
    pdf.cell(0, 8, f"Total Duration: {sum(durations):.2f} seconds", ln=True)
    pdf.cell(0, 8, f"Average Duration: {avg_duration:.2f} seconds", ln=True)
    pdf.cell(0, 8, f"Shortest Speech: {min_duration:.2f} seconds", ln=True)
    pdf.cell(0, 8, f"Longest Speech: {max_duration:.2f} seconds", ln=True)
    pdf.multi_cell(0, 8, safe_text(f"Emotion Transitions: {emotion_transitions}"))
    pdf.ln(4)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, safe_text("Voice Emotion Distribution:"), ln=True)
    pdf.set_font("Arial", size=12)
    for label, count in voice_counts.items():
        percent = count / len(voice_emotions) * 100
        pdf.cell(0, 8, safe_text(f"  - {label}: {count} ({percent:.1f}%)"), ln=True)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, safe_text("Visual Emotion Distribution:"), ln=True)
    pdf.set_font("Arial", size=12)
    for label, count in visual_counts.items():
        percent = count / len(visual_emotions) * 100
        pdf.cell(0, 8, safe_text(f"  - {label}: {count} ({percent:.1f}%)"), ln=True)

    buf = draw_bar_chart(voice_counts, f"{speaker} - Voice Emotion Chart")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(buf.read())
        tmp.flush()
        pdf.image(tmp.name, x=10, w=100)
    buf.close()
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, safe_text("Speech Details:"), ln=True)
    pdf.set_font("Arial", size=12)
    for idx, speech in enumerate(speeches, start=1):
        start = speech["start"]
        end = speech["end"]
        text = speech["text"].strip() or "[No text]"
        voice_emotion = speech["voice_emotion"]["label"]
        visual_emotion = speech["visual_emotion"]["label"]

        pdf.multi_cell(0, 8, safe_text(f"{idx}. [{start:.2f} - {end:.2f}]"))
        pdf.multi_cell(0, 8, safe_text(f"   Speech: {text}"))
        pdf.multi_cell(0, 8, safe_text(f"   Voice Emotion: {voice_emotion}"))
        pdf.multi_cell(0, 8, safe_text(f"   Visual Emotion: {visual_emotion}"))
        pdf.ln(3)

pdf.output("advanced_speech_report.pdf")
print("PDF successfully created: advanced_speech_report.pdf")
