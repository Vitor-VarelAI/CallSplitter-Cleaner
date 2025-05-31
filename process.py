import os
import shutil
from pydub import AudioSegment, silence
import whisper
from typing import Tuple, List
from datetime import datetime
import glob

# Configurações
INPUT_DIR = "/Users/vitorvarela/Documents/vozes-data/mp3"
BASE_OUTPUT_DIR = "output"
GUARDAR_SUSPEITAS = True  # Guardar segmentos que não passaram no filtro

# Parâmetros de processamento para arquivos longos (3-4h)
MIN_CALL_DURATION = 30      # segundos (aumentado para evitar chamadas muito curtas)
SILENCE_THRESH = -40        # dB (mais sensível ao silêncio)
MIN_SILENCE_LEN = 10000     # ms (10 segundos de silêncio mínimo para dividir)
KEEP_SILENCE = 1000         # ms (1 segundo de silêncio mantido)
WHISPER_MODEL = "small"     # Modelo Whisper a ser usado (base, small, medium, etc.)

# Criar estrutura de pastas com data de hoje
hoje = datetime.now().strftime("%Y-%m-%d")
OUTPUT_DIR = os.path.join(BASE_OUTPUT_DIR, hoje, "chamadas")
SUSPECT_DIR = os.path.join(BASE_OUTPUT_DIR, hoje, "suspeitas")
LOG_DIR = os.path.join(BASE_OUTPUT_DIR, hoje, "logs")

def limpar_pasta(pasta):
    """Remove todos os arquivos de uma pasta"""
    if os.path.exists(pasta):
        for arquivo in glob.glob(os.path.join(pasta, '*')):
            try:
                if os.path.isfile(arquivo):
                    os.unlink(arquivo)
                elif os.path.isdir(arquivo):
                    shutil.rmtree(arquivo)
            except Exception as e:
                print(f"Erro ao limpar {arquivo}: {e}")

def criar_diretorios():
    """Cria os diretórios necessários limpando os existentes"""
    # Criar diretório base de saída se não existir
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    
    # Limpar diretórios existentes
    limpar_pasta(OUTPUT_DIR)
    limpar_pasta(SUSPECT_DIR)
    limpar_pasta(LOG_DIR)
    
    # Criar diretórios
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    if GUARDAR_SUSPEITAS:
        os.makedirs(SUSPECT_DIR, exist_ok=True)

# Inicializar diretórios
criar_diretorios()

# Inicializar modelo Whisper
print(f"A carregar o modelo Whisper ({WHISPER_MODEL})...")
model = whisper.load_model(WHISPER_MODEL)

# Configurar opções de transcrição para melhor desempenho
transcribe_options = {
    'language': 'pt',
    'fp16': False,  # Mais estável em CPUs mais antigas
    'task': 'transcribe',
    'temperature': 0.0,  # Menos criatividade, mais precisão
}

def calcular_confianca(texto: str) -> Tuple[int, str, str]:
    """
    Calcula a pontuação de confiança com base nas frases-chave.
    Retorna uma tupla com (pontuação, nível_de_confiança, motivo)
    """
    texto = texto.lower()
    pontos = 0
    
    # Frases que indicam início de chamada
    frases_inicio = [
        "posso ser útil", 
        "está a falar com", 
        "sou o vitor",
        "bom dia", 
        "boa noite",
        "boa tarde"
    ]
    
    # Verificar se parece ser uma chamada real
    tem_inicio_chamada = any(phrase in texto for phrase in frases_inicio)
    tem_conversa = len(texto.split()) > 10  # Pelo menos 10 palavras
    
    if not tem_inicio_chamada and not tem_conversa:
        return (0, "rejeitado", "sem início de chamada e texto curto")
        
    if tem_inicio_chamada:
        pontos += 1
    
    # Frases que aumentam a confiança
    if any(phrase in texto for phrase in ["bom dia", "boa noite", "boa tarde"]):
        pontos += 1
    if any(phrase in texto for phrase in ["posso ser útil", "está a falar com", "sou o vitor"]):
        pontos += 1
    
    # Se tiver bastante texto, aumenta a confiança
    if len(texto.split()) > 20:
        pontos += 1
    
    # Determinar nível de confiança
    if pontos >= 3:
        return (pontos, "alta", "múltiplos indicadores de chamada")
    elif pontos == 2:
        return (pontos, "média", "alguns indicadores de chamada")
    elif pontos == 1:
        return (pontos, "baixa", "poucos indicadores de chamada")
    return (0, "rejeitado", "sem indicadores suficientes")

def processar_audio(arquivo_entrada: str) -> None:
    """Processa um arquivo de áudio, dividindo por silêncio e classificando cada segmento."""
    print(f"\nProcessando: {os.path.basename(arquivo_entrada)}")
    
    try:
        # Carregar áudio
        audio = AudioSegment.from_file(arquivo_entrada)
        audio = audio.set_channels(1).set_frame_rate(16000)
        
        # Dividir por silêncio
        chunks = silence.split_on_silence(
            audio,
            silence_thresh=SILENCE_THRESH,        # Limiar de silêncio em dB
            min_silence_len=MIN_SILENCE_LEN,     # ms (10 segundos de silêncio mínimo)
            keep_silence=KEEP_SILENCE          # ms (1 segundo de silêncio mantido)
        )
        
        print(f"Encontrados {len(chunks)} segmentos no arquivo.")
        
        for i, chunk in enumerate(chunks, 1):
            # Criar arquivo temporário para o chunk
            temp_path = f"temp_{i}.wav"
            chunk.export(temp_path, format="wav")
            
            try:
                # Transcrever com Whisper (usando opções otimizadas)
                try:
                    print(f"  - Transcrevendo segmento {i} ({len(chunk)/1000:.1f}s)...")
                    resultado = model.transcribe(
                        temp_path,
                        **transcribe_options
                    )
                    texto = resultado["text"].strip()
                except Exception as e:
                    print(f"  - Erro na transcrição: {str(e)}")
                    texto = ""
                
                # Calcular confiança
                pontos, confianca, motivo = calcular_confianca(texto)
                
                # Determinar destino do arquivo
                # Se for uma chamada clara ou tiver mais de 30 segundos, salva como chamada
                if confianca in ["alta", "média"] or len(chunk) > 30000:  # 30 segundos
                    destino = OUTPUT_DIR
                    prefixo = "call"
                    print(f"  - Segmento {i}: {confianca.upper()} ({len(chunk)/1000:.1f}s) - {motivo}")
                # Se for curto e de baixa confiança, ignora
                elif len(chunk) < 15000:  # Menos de 15 segundos
                    print(f"  - Segmento {i} muito curto ({len(chunk)/1000:.1f}s), ignorando...")
                    continue
                # Se for longo mas de baixa confiança, salva como suspeito
                elif GUARDAR_SUSPEITAS and len(chunk) > 15000:  # Mais de 15 segundos
                    destino = SUSPECT_DIR
                    prefixo = "suspeito"
                    print(f"  - Segmento {i} SUSPEITO: {motivo} ({len(chunk)/1000:.1f}s)")
                else:
                    print(f"  - Segmento {i} ignorado: {motivo} ({len(chunk)/1000:.1f}s)")
                    continue
                
                # Salvar áudio
                nome_arquivo = f"{prefixo}_{os.path.splitext(os.path.basename(arquivo_entrada))[0]}_{i:03d}.wav"
                caminho_saida = os.path.join(destino, nome_arquivo)
                chunk.export(caminho_saida, format="wav")
                
                # Salvar log
                nome_log = f"{prefixo}_{os.path.splitext(os.path.basename(arquivo_entrada))[0]}_{i:03d}.log"
                caminho_log = os.path.join(LOG_DIR, nome_log)
                
                with open(caminho_log, "w", encoding="utf-8") as f:
                    f.write(f"Arquivo: {os.path.basename(arquivo_entrada)}\n")
                    f.write(f"Segmento: {i}\n")
                    f.write(f"Status: {'[ACEITE]' if pontos > 0 else '[SUSPEITO]'}\n")
                    f.write(f"Confiança: {confianca} ({pontos}/3 pontos)\n")
                    f.write(f"Duração: {len(chunk)/1000:.2f} segundos\n")
                    f.write("\nTranscrição:\n")
                    f.write(texto)
                
                print(f"  - Segmento {i}: {confianca.upper()} ({len(chunk)/1000:.1f}s)")
                
            except Exception as e:
                print(f"Erro ao processar segmento {i}: {str(e)}")
            finally:
                # Limpar arquivo temporário
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
    except Exception as e:
        print(f"Erro ao processar {arquivo_entrada}: {str(e)}")

def main():
    print("=== CallSplitter v3.0 - Filtro Inteligente com Confiança ===")
    print(f"Data de processamento: {hoje}")
    print(f"Diretório de entrada: {os.path.abspath(INPUT_DIR)}")
    print(f"Diretório de saída: {os.path.abspath(os.path.join(BASE_OUTPUT_DIR, hoje))}")
    print(f"Guardar suspeitas: {'Sim' if GUARDAR_SUSPEITAS else 'Não'}")
    
    # Verificar arquivos para processar
    arquivos = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.mp3', '.wav'))]
    
    if not arquivos:
        print("Nenhum arquivo de áudio encontrado no diretório de entrada.")
        return
    
    print(f"\nEncontrados {len(arquivos)} arquivos para processar.")
    
    # Processar cada arquivo
    for arquivo in arquivos:
        processar_audio(os.path.join(INPUT_DIR, arquivo))
    
    print("\nProcessamento concluído!")
    print(f"- Arquivos processados: {len(arquivos)}")
    print(f"- Chamadas válidas: {len([f for f in os.listdir(OUTPUT_DIR) if f.startswith('call_')])}")
    if GUARDAR_SUSPEITAS:
        print(f"- Segmentos suspeitos: {len([f for f in os.listdir(SUSPECT_DIR) if f.startswith('suspeito_')])}")

if __name__ == "__main__":
    main()
