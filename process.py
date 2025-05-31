import os
from pydub import AudioSegment, silence
from datetime import datetime

INPUT_DIR = "/Users/vitorvarela/Documents/vozes-data/mp3"
OUTPUT_DIR = "output/calls"
LOG_DIR = "output/logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def split_and_clean(file_path, silence_thresh=-40, min_silence_len=10000):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1).set_frame_rate(16000)

    chunks = silence.split_on_silence(
        audio,
        silence_thresh=silence_thresh,
        min_silence_len=min_silence_len,
        keep_silence=1000
    )

    for i, chunk in enumerate(chunks):
        call_path = os.path.join(OUTPUT_DIR, f"call_{i+1:03}.wav")
        chunk.export(call_path, format="wav")
        with open(os.path.join(LOG_DIR, f"call_{i+1:03}.log"), "w") as f:
            f.write(f"Duração: {len(chunk) / 1000:.2f} segundos\n")

def main():
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".mp3") or file.endswith(".wav"):
            print(f"Processando: {file}")
            split_and_clean(os.path.join(INPUT_DIR, file))

if __name__ == "__main__":
    main()
