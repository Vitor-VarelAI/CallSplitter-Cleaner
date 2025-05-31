# CallSplitter-Cleaner v3.0 — Filtro Inteligente com Confiança

Este sistema processa ficheiros `.mp3` longos e identifica **chamadas reais com base em padrões reais de fala do Vitor Varela**. Utiliza Whisper para transcrever, analisa expressões típicas e classifica cada segmento com um nível de confiança.

---

## 🚀 Funcionalidades

- ✂️ Divide gravações longas em segmentos com base no silêncio
- 🧠 Transcreve cada segmento com Whisper (modelo `base`)
- ✅ Verifica se o texto inclui frases como:
  - "posso ser útil" → obrigatório
  - "bom dia" ou "boa noite" → aumenta confiança
  - "está a falar com" ou "sou o vitor " → ainda mais confiança
- 📂 Guarda apenas os segmentos classificados como chamados reais
- 📝 Cria logs com transcrição e nível de confiança
- ❗ (Opcional) Guarda segmentos ignorados em `output/suspeitas/`

---

## 📁 Estrutura do projeto

```
CallSplitter-Cleaner/
├── input/                   # Onde colocas os ficheiros .mp3
├── output/
│   ├── calls/               # Chamadas reais aceites
│   ├── suspeitas/           # (Opcional) Partes ignoradas para revisão
│   └── logs/                # Logs com transcrição e confiança
├── process_v3.py            # Script principal
└── README_v3.md             # Este ficheiro
```

---

## ⚙️ Instalação

1. Ativa o ambiente virtual:
```bash
source venv/bin/activate
```

2. Instala as dependências:
```bash
pip install pydub ffmpeg-python openai-whisper
```

3. Garante que tens `ffmpeg` instalado:
```bash
brew install ffmpeg
```

---

## ▶️ Como usar

1. Coloca os ficheiros `.mp3` dentro de `input/`
2. Corre o script:
```bash
python process_v3.py
```

---

## 🧠 Como funciona a filtragem

| Frase Detetada             | Peso     |
|---------------------------|----------|
| “posso ser útil”          | 1 ponto (obrigatório) |
| “bom dia” ou “boa noite”  | +1 ponto |
| “está a falar com” ou “sou o vitor” | +1 ponto |

---

## 📊 Níveis de Confiança

| Score | Confiança | Resultado  |
|-------|-----------|------------|
| 3     | Alta      | Guardado   |
| 2     | Média     | Guardado   |
| 1     | Mínima    | Guardado   |
| 0     | Rejeitado | Ignorado (pode ser guardado em `suspeitas/`) |

---

## 📝 Exemplo de Log

```log
[ACEITE] Chunk 3
Texto: bom dia, está a falar com o Vitor Varela, posso ser útil.
Confiança: alta
Duração: 14.2 segundos
```

---

## ❗ Guardar Suspeitas (opcional)

No topo do `process_v3.py` podes ativar:
```python
GUARDAR_SUSPEITAS = True
```

Assim, segmentos ignorados serão guardados em `output/suspeitas/` para análise futura.

---

## 💡 Sugestões Futuras

- Exportar transcrições em `.csv`
- Criar UI com Gradio
- Implementar modo batch para múltiplos dias
- Ligar a base de dados para histórico

---

Criado por Vitor Varela 🧠📞  
Com o CallSplitter, a tua voz é o gatilho da inteligência.
