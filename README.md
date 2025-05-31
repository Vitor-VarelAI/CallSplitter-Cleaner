# CallSplitter-Cleaner

Sistema para processar gravações longas de chamadas (ex: 4h), dividir automaticamente por chamadas, limpar o áudio, transcrever e analisar para preparar para processamento posterior.

## 🚀 Funcionalidades
- **Processamento em Lote Robusto**: Processa múltiplos arquivos de áudio localizados no diretório de entrada.
- **Detecção de Silêncio Configurável**: Permite ajustar o limiar de silêncio (dBFS) e a duração mínima do silêncio (ms) através de parâmetros na linha de comando, para otimizar a divisão das chamadas.
- **Divisão Automática de Chamadas**: Segmenta automaticamente as gravações longas em chamadas individuais com base nos períodos de silêncio detectados.
- **Normalização de Áudio**: Converte os segmentos de áudio para o formato WAV (mono, 16kHz), ideal para sistemas de transcrição.
- **Transcrição Automática de Áudio**: Utiliza a biblioteca `openai-whisper` (modelo "small" por padrão) para transcrever cada segmento de chamada detectado.
- **Análise de Transcrição**:
    - Detecção de frases de introdução padrão.
    - Cálculo de um score de confiança e nível de confiança ("alta", "média", "baixa", "rejeitado") para cada transcrição.
- **Output Detalhado em JSON**: Para cada segmento de chamada, gera um arquivo JSON contendo:
    - Metadados do arquivo (nome, duração).
    - Resultados da análise de confiança (score, nível, razão).
    - Informações sobre frases de introdução detectadas.
    - A transcrição completa.
    - Segmentos da transcrição com timestamps individuais.
- **Logging Abrangente**:
    - Gera um log principal (`batch_process.log`) no diretório de logs, registrando todas as operações do lote, erros e um sumário do processamento.
    - Cria logs individuais para cada segmento de áudio processado (ex: `arquivooriginal_call_001.log`) e para arquivos onde nenhuma atividade de voz foi detectada (ex: `arquivooriginal_empty.log`).
- **Exportação Organizada e Datada**: Salva os arquivos de áudio processados, transcrições JSON e logs em subdiretórios organizados pela data da execução (ex: `output/YYYY-MM-DD/chamadas/`, `output/YYYY-MM-DD/logs/`).

## 📁 Estrutura de Diretórios
- `input/`: Diretório padrão para colocar os arquivos de áudio longos (`.mp3` ou `.wav`).
- `output/YYYY-MM-DD/`: Diretório base para os resultados de uma execução específica, onde `YYYY-MM-DD` é a data da execução.
    - `chamadas/`: Contém os segmentos de áudio processados (`.wav`) e os seus respectivos arquivos de transcrição e análise (`.json`).
        - Exemplo: `somefile_call_001.wav`, `somefile_call_001.json`
    - `logs/`: Contém os arquivos de log da execução.
        - `batch_process.log`: Log principal com o registro de todas as operações do processamento em lote.
        - Logs individuais por segmento de chamada original (ex: `somefile_call_001.log`).
        - Logs para arquivos originais sem atividade de voz detectada (ex: `somefile_empty.log`).
- `process.py`: O script principal para executar o processamento.

## 🧪 Requisitos
- Python 3.9+
- **FFmpeg**: Essencial para o processamento de áudio. O FFmpeg deve estar instalado no sistema e acessível através do PATH. Muitos sistemas de gerenciamento de pacotes podem instalá-lo (ex: `sudo apt install ffmpeg` no Debian/Ubuntu, `brew install ffmpeg` no macOS).
- Dependências Python (instalar via pip):
  ```bash
  pip install pydub openai-whisper
  ```
  - **Nota sobre Whisper**: Os modelos do Whisper (ex: "small") são descarregados automaticamente na primeira utilização e armazenados em cache no diretório `~/.cache/whisper` (ou no local padrão do seu sistema operacional para cache de aplicações).

## ▶️ Como usar

O script é executado através da linha de comando. Após a segmentação de cada chamada, a transcrição e análise são realizadas automaticamente.

**Comando básico (usando valores padrão):**
```bash
python process.py
```
Este comando irá:
1. Procurar por arquivos de áudio no diretório `input/`.
2. Criar um diretório de saída datado (ex: `output/YYYY-MM-DD/`).
3. Salvar os segmentos de áudio processados em `output/YYYY-MM-DD/chamadas/`.
4. Salvar os logs da execução em `output/YYYY-MM-DD/logs/`.
5. Transcrever cada segmento de áudio e guardar o resultado num arquivo `.json` correspondente em `output/YYYY-MM-DD/chamadas/`.
6. Utilizar os parâmetros de detecção de silêncio e modelo Whisper padrão ("small").

**Argumentos da Linha de Comando:**

O script aceita os seguintes argumentos para personalizar o processamento:

- `--input_dir DIRETORIO_ENTRADA`: Especifica o diretório que contém os arquivos de áudio a serem processados.
  - Padrão: `input/`
- `--output_dir DIRETORIO_SAIDA_BASE`: Especifica o diretório base onde as pastas datadas de saída (`YYYY-MM-DD/chamadas/`) serão criadas.
  - Padrão: `output`
- `--log_dir DIRETORIO_LOG_BASE`: Especifica o diretório base onde as pastas datadas de log (`YYYY-MM-DD/logs/`) serão criadas.
  - Padrão: `output` (os logs ficarão dentro de `output/YYYY-MM-DD/logs/`)
- `--silence_thresh DBFS_SILENCIO`: Define o limiar de silêncio em dBFS (decibéis relativos à escala total). Valores mais baixos (ex: -50) são mais sensíveis e podem detectar silêncios mais sutis.
  - Padrão: `-40`
- `--min_silence_len MS_SILENCIO_MINIMO`: Define a duração mínima de um período de silêncio (em milissegundos) para que seja considerado um ponto de divisão entre chamadas.
  - Padrão: `10000` (10 segundos)

**Exemplos de Uso:**

1.  **Processar áudios usando os diretórios e parâmetros padrão:**
    ```bash
    python process.py
    ```

2.  **Especificar diretórios base de saída/log diferentes e ajustar os parâmetros de detecção de silêncio:**
    ```bash
    python process.py --input_dir ./minhas_gravacoes --output_dir ./saida_geral --log_dir ./saida_geral/logs_processamento --silence_thresh -35 --min_silence_len 8000
    ```
    *(Neste exemplo, os arquivos WAV e JSON irão para `./saida_geral/YYYY-MM-DD/chamadas/` e os logs para `./saida_geral/logs_processamento/YYYY-MM-DD/logs/`)*

3.  **Apenas mudar o diretório de entrada, mantendo os outros padrões:**
    ```bash
    python process.py --input_dir /media/shared/audio_source
    ```

## 🏛️ Estrutura do Output JSON

Para cada segmento de áudio (`.wav`) processado e transcrito com sucesso, um arquivo `.json` correspondente é gerado.

**Exemplo de JSON de Sucesso (`somefile_call_001.json`):**
```json
{
    "filename": "somefile_call_001.wav",
    "duration": 123.45,
    "confidence_score": 3,
    "confidence_level": "alta",
    "reason": "Introduction detected, Transcript >20 words",
    "intro_detected": true,
    "intro_phrases": [
        "bom dia",
        "posso ser útil"
    ],
    "transcript": "Bom dia, posso ser útil? Sim, gostaria de falar sobre...",
    "segments": [
        {
            "id": 0,
            "seek": 0,
            "start": 0.0,
            "end": 3.5,
            "text": " Bom dia, posso ser útil?",
            "tokens": [ /* ... */ ],
            "temperature": 0.0,
            "avg_logprob": -0.5,
            "compression_ratio": 1.5,
            "no_speech_prob": 0.1
        },
        {
            "id": 1,
            "seek": 0,
            "start": 3.5,
            "end": 5.0,
            "text": " Sim, gostaria de falar sobre...",
            "tokens": [ /* ... */ ],
            "temperature": 0.0,
            "avg_logprob": -0.4,
            "compression_ratio": 1.5,
            "no_speech_prob": 0.05
        }
        // ... mais segmentos
    ]
}
```

**Exemplo de JSON de Erro na Transcrição (`somefile_call_002.json`):**
```json
{
    "filename": "somefile_call_002.wav",
    "error": true,
    "error_message": "Whisper transcription failed for somefile_call_002.wav.",
    "transcript": "",
    "segments": []
}
```
(Nota: O campo `duration` pode ou não estar presente em caso de erro de transcrição, dependendo se a falha ocorreu antes ou depois da sua medição.)
