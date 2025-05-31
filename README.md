# CallSplitter-Cleaner

Sistema para processar gravações longas de chamadas (ex: 4h), dividir automaticamente por chamadas, limpar o áudio e preparar para transcrição.

## 🚀 Funcionalidades
- **Processamento em Lote Robusto**: Processa múltiplos arquivos de áudio localizados no diretório de entrada.
- **Detecção de Silêncio Configurável**: Permite ajustar o limiar de silêncio (dBFS) e a duração mínima do silêncio (ms) através de parâmetros na linha de comando, para otimizar a divisão das chamadas.
- **Divisão Automática de Chamadas**: Segmenta automaticamente as gravações longas em chamadas individuais com base nos períodos de silêncio detectados.
- **Normalização de Áudio**: Converte os segmentos de áudio para o formato WAV (mono, 16kHz), ideal para sistemas de transcrição como Whisper.
- **Logging Abrangente**:
    - Gera um log principal (`batch_process.log`) no diretório de logs, registrando todas as operações do lote, erros e um sumário do processamento.
    - Cria logs individuais para cada segmento de áudio processado (ex: `arquivooriginal_call_001.log`) e para arquivos onde nenhuma atividade de voz foi detectada (ex: `arquivooriginal_empty.log`).
- **Exportação Organizada**: Salva os arquivos de áudio processados e os logs em diretórios de saída configuráveis.

## 📁 Estrutura
- `input/`: Diretório padrão para colocar os arquivos de áudio longos (`.mp3` ou `.wav`).
- `output/calls/`: Diretório padrão onde as chamadas divididas e limpas são salvas.
- `output/logs/`: Diretório padrão para os arquivos de log. Contém:
    - `batch_process.log`: Log principal com o registro de todas as operações do processamento em lote.
    - Logs individuais por segmento de chamada (ex: `nomeoriginal_call_001.log`).
    - Logs para arquivos sem atividade de voz detectada (ex: `nomeoriginal_empty.log`).
- `process.py`: O script principal para executar o processamento.

## 🧪 Requisitos
- Python 3.9+
- **FFmpeg**: Essencial para o processamento de áudio. O FFmpeg deve estar instalado no sistema e acessível através do PATH. Muitos sistemas de gerenciamento de pacotes podem instalá-lo (ex: `sudo apt install ffmpeg` no Debian/Ubuntu, `brew install ffmpeg` no macOS).
- Dependências Python (instalar via pip):
  ```bash
  pip install pydub
  ```
  (Nota: `ffmpeg-python` não é diretamente usado pelo script, `pydub` invoca o executável `ffmpeg`.)

## ▶️ Como usar

O script é executado através da linha de comando.

**Comando básico (usando valores padrão):**
```bash
python process.py
```
Este comando irá procurar por arquivos de áudio no diretório `input/`, salvará os segmentos processados em `output/calls/` e os logs em `output/logs/`, utilizando os parâmetros de detecção de silêncio padrão.

**Argumentos da Linha de Comando:**

O script aceita os seguintes argumentos para personalizar o processamento:

- `--input_dir DIRETORIO_ENTRADA`: Especifica o diretório que contém os arquivos de áudio a serem processados.
  - Padrão: `input/`
- `--output_dir DIRETORIO_SAIDA_CALLS`: Especifica o diretório onde os segmentos de áudio processados (chamadas divididas) serão salvos.
  - Padrão: `output/calls/`
- `--log_dir DIRETORIO_LOGS`: Especifica o diretório onde todos os arquivos de log serão salvos (incluindo o `batch_process.log` e logs individuais).
  - Padrão: `output/logs/`
- `--silence_thresh DBFS_SILENCIO`: Define o limiar de silêncio em dBFS (decibéis relativos à escala total). Valores mais baixos (ex: -50) são mais sensíveis e podem detectar silêncios mais sutis.
  - Padrão: `-40`
- `--min_silence_len MS_SILENCIO_MINIMO`: Define a duração mínima de um período de silêncio (em milissegundos) para que seja considerado um ponto de divisão entre chamadas.
  - Padrão: `10000` (10 segundos)

**Exemplos de Uso:**

1.  **Processar áudios usando os diretórios e parâmetros padrão:**
    ```bash
    python process.py
    ```

2.  **Especificar diretórios de entrada e saída diferentes e ajustar os parâmetros de detecção de silêncio:**
    ```bash
    python process.py --input_dir ./minhas_gravacoes --output_dir ./chamadas_processadas --log_dir ./logs_de_processamento --silence_thresh -35 --min_silence_len 8000
    ```

3.  **Apenas mudar o diretório de entrada, mantendo os outros padrões:**
    ```bash
    python process.py --input_dir /media/shared/audio_source
    ```
