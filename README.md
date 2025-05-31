# CallSplitter-Cleaner v2.1

Processa ficheiros `.mp3` longos (ex: 4h), divide com base em silêncio e **guarda apenas as chamadas reais**, com base na forma como o Vitor fala.

---

## 🚀 Funcionalidades

- 📤 Divide gravações por silêncio (>10s)
- 🧠 Usa Whisper para transcrever cada segmento
- ✅ Guarda apenas as chamadas que:
  - contêm `"posso ser útil"`
  - e `"bom dia"` ou `"boa noite"`
  - e `"está a falar com"` ou `"sou o vitor"`
- 📝 Cria `.log` com a transcrição e duração de cada chamada

---

## 📁 Estrutura

```
CallSplitter-Cleaner/
├── input/             # coloca aqui os teus .mp3
├── output/
│   ├── calls/        # onde ficam as chamadas reais
│   └── logs/         # onde ficam os .log de cada chamada
├── process.py        # script principal (v2.1 com Whisper)
├── README.md        # este ficheiro
└── venv/            # ambiente virtual (opcional)
```

## 🛠️ Requisitos

- Python 3.9+
- ffmpeg (para processamento de áudio)
- Whisper (para transcrição)

### Instalação

