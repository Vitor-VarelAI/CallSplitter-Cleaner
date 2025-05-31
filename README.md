# CallSplitter-Cleaner

Sistema para processar gravações longas de chamadas (ex: 4h), dividir automaticamente por chamadas, limpar o áudio e preparar para transcrição.

## 🚀 Funcionalidades
- Conversão automática para WAV (mono, 16kHz)
- Deteção de silêncio prolongado (ex: >10s) para separar chamadas
- Exportação de chamadas como `call_001.wav`, `call_002.wav`...
- Preparação para integração com Whisper ou outro sistema de transcrição

## 📁 Estrutura
- `input/`: colocar aqui os `.mp3` ou `.wav` longos
- `output/calls/`: chamadas divididas e limpas
- `output/logs/`: logs e informações técnicas por chamada

## 🧪 Requisitos
- Python 3.9+
- Instalar dependências:
```bash
pip install pydub ffmpeg-python
```

## ▶️ Como usar
```bash
python process.py
```

