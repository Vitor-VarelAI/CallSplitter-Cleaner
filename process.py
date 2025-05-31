import os
import argparse
import subprocess
import sys
import logging
import json # Added json import
# Attempt to import whisper at the top level.
# The check in main() will handle if it's not found and script needs to exit.
try:
    import whisper
except ImportError:
    whisper = None # Ensure whisper is defined so script doesn't crash if not installed

from pydub import AudioSegment, silence
from pydub import exceptions as pydub_exceptions
from datetime import datetime

WHISPER_MODEL = None # Global variable to store the loaded Whisper model
DEFAULT_INTRO_PHRASES = [
    "posso ser útil",
    "bom dia",
    "boa noite",
    "está a falar com",
    "sou o vitor"
]

# Default paths are now defined within the argument parser setup

def split_and_clean(file_path, output_dir, log_dir, logger, silence_thresh=-40, min_silence_len=10000):
    try:
        audio = AudioSegment.from_file(file_path)
    except pydub_exceptions.CouldntDecodeError as e:
        logger.error(f"Error decoding audio file {file_path}: {e}. Skipping.")
        return False # Indicate failure
    except FileNotFoundError:
        logger.error(f"Error: Audio file {file_path} not found. Skipping.")
        return False # Indicate failure
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading audio file {file_path}: {e}. Skipping.")
        return False # Indicate failure

    original_file_stem = os.path.splitext(os.path.basename(file_path))[0]
    exported_chunk_paths = [] # Initialize list to store paths of exported chunks

    audio = audio.set_channels(1).set_frame_rate(16000)

    chunks = silence.split_on_silence(
        audio,
        silence_thresh=silence_thresh,
        min_silence_len=min_silence_len,
        keep_silence=1000
    )

    if not chunks:
        logger.info(f"No voice activity detected in {file_path} based on current silence parameters. Duration: {len(audio) / 1000:.2f}s")
        with open(os.path.join(log_dir, f"{original_file_stem}_empty.log"), "w") as f:
            f.write(f"No voice activity detected. Duration: {len(audio) / 1000:.2f} segundos\n")
        return exported_chunk_paths # Return empty list, as processing was successful but no chunks

    for i, chunk in enumerate(chunks):
        call_path = os.path.join(output_dir, f"{original_file_stem}_call_{i+1:03}.wav")
        try:
            chunk.export(call_path, format="wav")
            exported_chunk_paths.append(call_path) # Add path if export is successful
            with open(os.path.join(log_dir, f"{original_file_stem}_call_{i+1:03}.log"), "w") as f:
                f.write(f"Duração: {len(chunk) / 1000:.2f} segundos\n")
        except Exception as export_e:
            logger.error(f"Failed to export chunk {i+1} for file {file_path}: {export_e}")
            # Optionally, decide if this constitutes a failure for the whole file
            # For now, we continue processing other chunks and will return those successfully exported

    if exported_chunk_paths: # Log only if some chunks were actually processed and exported
        logger.info(f"Successfully split {file_path} into {len(exported_chunk_paths)} chunks.")
    elif not chunks: # This case is already logged above, re-iterating for clarity or if we want different msg
        pass # No chunks found, already logged.
    else: # Chunks were found, but all failed to export.
        logger.error(f"All chunks for {file_path} failed to export.")
        # Depending on desired behavior, could return False here if any export fails implies total failure

    return exported_chunk_paths # Return the list of successfully exported chunk paths

def main():
    parser = argparse.ArgumentParser(description="Split audio files based on silence and process them.")
    parser.add_argument(
        "--input_dir",
        type=str,
        default="input/",
        help="Directory containing input audio files. Default: 'input/'"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output", # Changed default
        help="Base directory for dated output folders (e.g., 'output/YYYY-MM-DD/chamadas/'). Default: 'output'"
    )
    parser.add_argument(
        "--log_dir",
        type=str,
        default="output", # Changed default
        help="Base directory for dated log folders (e.g., 'output/YYYY-MM-DD/logs/'). Default: 'output'"
    )
    parser.add_argument(
        "--silence_thresh",
        type=int,
        default=-40,
        help="Silence threshold in dBFS (e.g., -40). Lower values detect quieter silences. Default: -40"
    )
    parser.add_argument(
        "--min_silence_len",
        type=int,
        default=10000,
        help="Minimum silence length in milliseconds (e.g., 10000 for 10 seconds). Default: 10000"
    )
    args = parser.parse_args()

    input_dir = args.input_dir
    base_output_dir_arg = args.output_dir # Base for YYYY-MM-DD/chamadas
    base_log_dir_arg = args.log_dir     # Base for YYYY-MM-DD/logs
    silence_thresh_arg = args.silence_thresh
    min_silence_len_arg = args.min_silence_len

    current_date_str = datetime.now().strftime('%Y-%m-%d')

    # Construct dated paths
    dated_calls_output_dir = os.path.join(base_output_dir_arg, current_date_str, 'chamadas')
    dated_log_output_dir = os.path.join(base_log_dir_arg, current_date_str, 'logs')

    # Create dated directories
    os.makedirs(dated_calls_output_dir, exist_ok=True)
    os.makedirs(dated_log_output_dir, exist_ok=True)

    # Setup Logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # Place batch_process.log inside the dated log directory
    batch_log_file_path = os.path.join(dated_log_output_dir, 'batch_process.log')

    # File Handler for batch_process.log
    fh = logging.FileHandler(batch_log_file_path) # Use new path
    fh.setLevel(logging.INFO)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO) # Log INFO and above to console

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    # Whisper Library Check - Now critical for the script to proceed if transcription features are to be used.
    if whisper is None:
        logger.critical("The 'openai-whisper' library is not installed. This script requires it for transcription features. Please install it by running: pip install openai-whisper")
        print("CRITICAL: The 'openai-whisper' library is not installed. This script requires it for transcription features. Please install it by running: pip install openai-whisper", file=sys.stderr)
        sys.exit(1) # Exit if whisper is not available
    else:
        logger.info("The 'openai-whisper' library is available.")

    # FFmpeg Check - now uses logger
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        if result.returncode != 0:
            logger.critical("FFmpeg command ran but indicated an error. FFmpeg is required.")
            raise FileNotFoundError # Treat as if not found for simplicity
        logger.info("FFmpeg found and version check successful.")
    except FileNotFoundError:
        logger.critical("Error: FFmpeg is not installed or not found in PATH. FFmpeg is required for audio processing.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        logger.critical(f"Error during FFmpeg version check: {e}. Ensure FFmpeg is correctly installed.")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred while checking for FFmpeg: {e}")
        sys.exit(1)

    if not os.path.isdir(input_dir):
        logger.error(f"Error: Input directory '{input_dir}' does not exist or is not a directory.")
        sys.exit(1)

    logger.info(f"Batch processing started. Input: '{input_dir}', WAVs Output: '{dated_calls_output_dir}', Logs: '{dated_log_output_dir}'")

    audio_files = [f for f in os.listdir(input_dir) if f.endswith((".mp3", ".wav"))]

    if not audio_files:
        logger.warning(f"No audio files (.mp3 or .wav) found in the input directory: {input_dir}")
        sys.exit(0)

    successful_files = 0
    failed_files = 0

    for file_name in audio_files: # Renamed 'file' to 'file_name' to avoid conflict
        full_file_path = os.path.join(input_dir, file_name)
        logger.info(f"Starting splitting phase for file: {file_name}")

        split_and_clean_result = [] # Default to empty list
        try:
            split_and_clean_result = split_and_clean(
                full_file_path,
                dated_calls_output_dir,
                dated_log_output_dir,
                logger,
                silence_thresh=silence_thresh_arg,
                min_silence_len=min_silence_len_arg
            )

            if isinstance(split_and_clean_result, list):
                successful_files += 1
                logger.info(f"Splitting phase successful for {file_name}. Found {len(split_and_clean_result)} potential audio chunks.")

                if not split_and_clean_result: # Empty list means no voice activity or no chunks exported
                    logger.info(f"No audio chunks were exported from {file_name} (e.g. no voice activity or export errors).")

                for chunk_wav_path in split_and_clean_result:
                    logger.info(f"Attempting transcription for chunk: {chunk_wav_path}")
                    transcription_result = transcribe_audio(chunk_wav_path, model_name="small", logger=logger)

                    json_file_name = os.path.splitext(os.path.basename(chunk_wav_path))[0] + ".json"
                    # JSONs for call chunks go into the dated_calls_output_dir alongside their WAVs
                    json_file_path = os.path.join(dated_calls_output_dir, json_file_name)

                    if transcription_result and "text" in transcription_result:
                        logger.info(f"Constructing JSON data for successful transcription of {chunk_wav_path}")
                        transcript_text = transcription_result.get('text', '')

                        duration_seconds = 0.0
                        try:
                            audio_segment = AudioSegment.from_file(chunk_wav_path)
                            duration_seconds = len(audio_segment) / 1000.0
                        except Exception as e_dur:
                            logger.warning(f"Could not get duration for {chunk_wav_path}: {e_dur}")

                        intro_detected, intro_phrases_found = detect_introduction(transcript_text, DEFAULT_INTRO_PHRASES, logger)
                        conf_score, conf_level, conf_reason = calcular_confianca(transcript_text, intro_phrases_found, logger)

                        json_data = {
                            "filename": os.path.basename(chunk_wav_path),
                            "duration": round(duration_seconds, 2),
                            "confidence_score": conf_score,
                            "confidence_level": conf_level,
                            "reason": conf_reason,
                            "intro_detected": intro_detected,
                            "intro_phrases": intro_phrases_found,
                            "transcript": transcript_text,
                            "segments": transcription_result.get('segments', [])
                        }
                        save_to_json(json_data, json_file_path, logger)

                        # Limit snippet length more carefully for debug log
                        snippet = transcript_text[:100].replace('\n', ' ') + "..." if transcript_text else "[empty transcript]"
                        logger.debug(f"Transcript snippet for {chunk_wav_path}: {snippet}")

                    else:
                        logger.error(f"Transcription failed for {chunk_wav_path}. Constructing error JSON.")
                        error_message = f"Whisper transcription failed for {os.path.basename(chunk_wav_path)}."
                        json_data = {
                            "filename": os.path.basename(chunk_wav_path),
                            "error": True,
                            "error_message": error_message,
                            "transcript": "",
                            "segments": []
                        }
                        save_to_json(json_data, json_file_path, logger)
            else: # split_and_clean returned False (or something other than a list)
                failed_files += 1
                logger.error(f"Splitting phase failed for {file_name}.")

        except Exception as e:
            logger.error(f"An unexpected error occurred during processing (including transcription) of file {file_name}: {e}. Skipping remaining steps for this file.")
            failed_files += 1 # Count as a failure for the main file processing if an unhandled exception occurs

        # This log might be redundant if the above logs are clear, or could summarize file outcome
        # logger.info(f"Finished all processing for file: {file_name}.")

    logger.info("\n--- Processing Summary ---")
    logger.info(f"Successfully processed (split phase) files: {successful_files}")
    logger.info(f"Failed (split) files: {failed_files}")
    logger.info(f"Total files attempted for splitting: {len(audio_files)}")
    logger.info("------------------------")
    logger.info("Batch processing (splitting phase) completed.")

# --- Whisper Transcription Function ---
def transcribe_audio(audio_file_path: str, model_name: str = "small", logger=None): # Added logger type hint for clarity
    """
    Transcribes an audio file using Whisper.
    Loads the model once and reuses it for subsequent calls.
    """
    global WHISPER_MODEL

    if logger is None:
        # This fallback logger setup is basic and primarily for standalone testing of the function.
        # In the main script flow, `logger` should always be provided by `main()`.
        logger = logging.getLogger(__name__ + ".transcribe_audio") # Unique name for this logger instance
        if not logger.handlers: # Check if handlers are already configured
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO) # Default level for this standalone logger


    if WHISPER_MODEL is None:
        if whisper is None:
            logger.critical("Whisper library is not imported/available. Cannot load model.")
            return None
        try:
            logger.info(f"Loading Whisper model '{model_name}'... This may take a while.")
            WHISPER_MODEL = whisper.load_model(model_name)
            logger.info(f"Whisper model '{model_name}' loaded successfully.")
        except Exception as e:
            logger.critical(f"Failed to load Whisper model '{model_name}': {e}")
            WHISPER_MODEL = None
            return None

    if WHISPER_MODEL:
        try:
            logger.info(f"Starting transcription for {audio_file_path} using model {model_name}...")
            result = WHISPER_MODEL.transcribe(audio_file_path, fp16=False)
            logger.info(f"Transcription successful for {audio_file_path}.")
            return result
        except Exception as e:
            logger.error(f"Whisper transcription failed for {audio_file_path}: {e}")
            return None
    else:
        logger.error("Whisper model is not available. Cannot transcribe.")
        return None

# --- Introduction Detection Function ---
def detect_introduction(transcript_text: str, intro_phrase_list: list, logger=None) -> tuple[bool, list[str]]:
    """
    Detects standard introduction phrases in a transcript.
    Returns a boolean indicating if an intro was detected and a list of detected phrases.
    """
    if logger is None: # Fallback logger setup
        logger = logging.getLogger(__name__ + ".detect_introduction")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG) # Set to DEBUG to see its messages by default if standalone

    detected_phrases = []
    if not transcript_text: # Handle empty or None transcript text
        if logger:
            logger.debug("Transcript text is empty. No introduction phrases to detect.")
        return False, []

    lower_transcript = transcript_text.lower()

    for phrase in intro_phrase_list:
        lower_phrase = phrase.lower()
        if lower_phrase in lower_transcript:
            detected_phrases.append(phrase) # Store original casing

    intro_detected_boolean = len(detected_phrases) > 0

    if logger:
        if intro_detected_boolean:
            logger.debug(f"Detected introduction phrases: {list(set(detected_phrases))}")
        else:
            logger.debug("No standard introduction phrases detected.")

    return intro_detected_boolean, list(set(detected_phrases))

# --- Confidence Calculation Function ---
def calcular_confianca(transcript_text: str, detected_intro_phrases: list, logger=None) -> tuple[int, str, str]:
    """
    Calculates a confidence score for the transcript based on detected introductions and word count.
    Returns the score, confidence level string, and a reason string.
    """
    if logger is None: # Fallback logger setup
        logger = logging.getLogger(__name__ + ".calcular_confianca")
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

    score = 0
    reasons = []

    # Criterion 1: Introduction Phrases
    if detected_intro_phrases and len(detected_intro_phrases) > 0:
        score += 1
        reasons.append("Introduction detected")

    # Criterion 2 & 3: Word Count
    # Use strip() to ensure whitespace-only strings are treated as empty for word count
    effective_transcript_text = transcript_text.strip() if transcript_text else ""
    num_words = len(effective_transcript_text.split()) if effective_transcript_text else 0

    if num_words > 20:
        score += 2 # Meets both >10 and >20 criteria
        reasons.append("Transcript >20 words")
    elif num_words > 10:
        score += 1 # Meets >10 criterion
        reasons.append("Transcript >10 words")

    # Cap score at 3 (though current logic naturally does this if intro + >20 words)
    score = min(score, 3)

    # Determine Confidence Level String
    if score >= 3: # Should only be 3 with current logic
        confidence_level = "alta"
    elif score == 2:
        confidence_level = "média"
    elif score == 1:
        confidence_level = "baixa"
    else: # score == 0
        confidence_level = "rejeitado"

    # Format Reason String
    if not reasons: # Score is 0
        if not effective_transcript_text:
            reason_str = "Empty or whitespace-only transcript"
        else: # Transcript has some words but not enough, and no intro
            reason_str = f"Short transcript ({num_words} words) and no intro phrases"
    else:
        reason_str = ", ".join(reasons)

    if logger:
        logger.debug(f"Confidence calculated: Score {score}, Level '{confidence_level}', Reason(s) '{reason_str}'")

    return score, confidence_level, reason_str

# --- JSON Saving Function ---
def save_to_json(data_to_save: dict, json_file_path: str, logger=None) -> bool:
    """
    Saves the given dictionary data to a JSON file.
    Returns True on success, False on failure.
    """
    if logger:
        logger.debug(f"Attempting to save data to JSON file: {json_file_path}")

    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        if logger:
            logger.info(f"Successfully saved JSON data to: {json_file_path}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Failed to save JSON to {json_file_path}: {e}")
        else: # Basic feedback if no logger
            print(f"Error: Failed to save JSON to {json_file_path}: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    main()
