import os
from pydub import AudioSegment, silence
from pydub.utils import which
import whisper

# Caminhos
INPUT_DIR = "/Users/vitorvarela/Documents/vozes-data/mp3"
OUTPUT_DIR = "output/calls"
LOG_DIR = "output/logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Ligação ao ffmpeg
AudioSegment.converter = which("ffmpeg")

# Carregar modelo Whisper
model = whisper.load_model("base")

# Transcrever ficheiro
def transcrever_whisper(audio_path):
    resultado = model.transcribe(audio_path, language="pt", fp16=False)
    return resultado["text"].strip().lower()

# Verificar se é chamada real
def is_chamada_real(texto):
    return (
        "posso ser útil" in texto and
        ("bom dia" in texto or "boa noite" in texto) and
        ("está a falar com" in texto or "sou o vitor" in texto)
    )

# Processar ficheiro
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
        temp_path = "temp.wav"
        chunk.export(temp_path, format="wav")

        texto = transcrever_whisper(temp_path)

        if is_chamada_real(texto):
            call_path = os.path.join(OUTPUT_DIR, f"call_{i+1:03}.wav")
            chunk.export(call_path, format="wav")
            with open(os.path.join(LOG_DIR, f"call_{i+1:03}.log"), "w") as f:
                f.write(f"Texto: {texto}\n")
                f.write(f"Duração: {len(chunk) / 1000:.2f} segundos\n")
        else:
            print(f"[IGNORADO] Chunk {i+1} não é uma chamada real. Texto: {texto[:80]}...")

def main():
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".mp3") or file.endswith(".wav"):
            print(f"Processando: {file}")
            split_and_clean(os.path.join(INPUT_DIR, file))

if __name__ == "__main__":
    main()

def main():
    for file in os.listdir(INPUT_DIR):
        if file.endswith(".mp3") or file.endswith(".wav"):
            print(f"Processando: {file}")
            split_and_clean(os.path.join(INPUT_DIR, file))

if __name__ == "__main__":
    main()
