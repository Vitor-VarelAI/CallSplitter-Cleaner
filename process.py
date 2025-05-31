import os
import argparse
import subprocess
import sys
import logging # Added for logging
from pydub import AudioSegment, silence
from pydub import exceptions as pydub_exceptions
from datetime import datetime

# Default paths are now defined within the argument parser setup

def split_and_clean(file_path, output_dir, log_dir, logger, silence_thresh=-40, min_silence_len=10000): # Added logger parameter
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
        return True

    for i, chunk in enumerate(chunks):
        call_path = os.path.join(output_dir, f"{original_file_stem}_call_{i+1:03}.wav")
        chunk.export(call_path, format="wav")
        with open(os.path.join(log_dir, f"{original_file_stem}_call_{i+1:03}.log"), "w") as f:
            f.write(f"Duração: {len(chunk) / 1000:.2f} segundos\n")
    logger.info(f"Successfully split {file_path} into {len(chunks)} chunks.")
    return True

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
        default="output/calls/",
        help="Directory to save processed audio chunks. Default: 'output/calls/'"
    )
    parser.add_argument(
        "--log_dir",
        type=str,
        default="output/logs/",
        help="Directory to save log files for processed chunks and the main batch log. Default: 'output/logs/'"
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
    output_dir = args.output_dir
    log_dir_path = args.log_dir # Renamed to avoid conflict with log_dir in split_and_clean
    silence_thresh_arg = args.silence_thresh
    min_silence_len_arg = args.min_silence_len

    # Create directories first, so log file can be created
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(log_dir_path, exist_ok=True)

    # Setup Logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    log_file_path = os.path.join(log_dir_path, 'batch_process.log')

    # File Handler for batch_process.log
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.INFO)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO) # Log INFO and above to console

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

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

    logger.info(f"Batch processing started. Input: '{input_dir}', Output: '{output_dir}', Logs: '{log_dir_path}'")

    audio_files = [f for f in os.listdir(input_dir) if f.endswith((".mp3", ".wav"))]

    if not audio_files:
        logger.warning(f"No audio files (.mp3 or .wav) found in the input directory: {input_dir}")
        sys.exit(0)

    successful_files = 0
    failed_files = 0

    for file in audio_files:
        full_file_path = os.path.join(input_dir, file)
        logger.info(f"Starting processing for file: {file}")
        success_status = False
        try:
            if split_and_clean(full_file_path, output_dir, log_dir_path, logger, # Pass logger
                               silence_thresh=silence_thresh_arg,
                               min_silence_len=min_silence_len_arg):
                successful_files += 1
                success_status = True
            else:
                failed_files += 1
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing file {file}: {e}. Skipping.")
            failed_files += 1
        logger.info(f"Finished processing for file: {file}. Success: {success_status}")

    logger.info("\n--- Processing Summary ---")
    logger.info(f"Successfully processed files: {successful_files}")
    logger.info(f"Failed files: {failed_files}")
    logger.info(f"Total files attempted: {len(audio_files)}")
    logger.info("------------------------")
    logger.info("Batch processing completed.")

if __name__ == "__main__":
    main()
