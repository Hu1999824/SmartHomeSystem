# Voice/audio/whisperAsr.py
from faster_whisper import WhisperModel
import time
import sys
from pathlib import Path
from typing import Optional

# === Path repair (supports running from any location in the repository & independent testing) ===
THIS_FILE = Path(__file__).resolve()            # .../Voice/audio/whisperAsr.py
VOICE_DIR = THIS_FILE.parent.parent              # .../Voice
REPO_ROOT = THIS_FILE.parents[2]                 # Repository Root

for p in [str(VOICE_DIR), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.append(p)

# === Configuration and Dependency Import ===
try:
    # Recommended definitions in Voice/config/settings.py:
    # ASR_MODEL_SIZE = "base"           # or "base.en" / "tiny" / "small" etc.
    # ASR_LANGUAGE   = None             # None=Auto; "zh"=Chinese; "en"=English
    from Voice.config.settings import ASR_MODEL_SIZE, ASR_LANGUAGE
except Exception:
    print("Warning: config.settings not found. Using default ASR_MODEL_SIZE='base', ASR_LANGUAGE=None")
    ASR_MODEL_SIZE = "base"
    ASR_LANGUAGE = None  # Auto-detect

# This is for standalone testing only in `__main__`; the main process calls its own recording function from `main.py`.
try:
    from Voice.audio.recordAudio import recordAudio
except Exception:
    print("Warning: Voice.audio.recordAudio not found. Standalone test will use a stub.")
    def recordAudio(filename: str = "test.wav", duration: int = 3) -> Optional[str]:
        print(f"[Stub] Please prepare the audio file manually: {filename} (will attempt to transcribe directly)")
        return filename if Path(filename).exists() else None


class WhisperAsr:
    """
    ASR (Automatic Speech Recognition) Component:
    - transcribe(audioFile): Transcribes using auto-detected or configured language
    - transcribeAudio(audioFile, language=None): Alias for compatibility; language overrides config
    """

    def __init__(self, modelSize: str = ASR_MODEL_SIZE):
        """
        Args:
            modelSize: Whisper model size, e.g., "tiny" / "base" / "small" / "base.en"
        """
        print(f"[ASR] Loading Whisper model '{modelSize}'... (Will download model on first run)")
        try:
            # Compatibility config: CPU + int8; for higher precision, change compute_type="int8_float16"/"float16"
            self.model = WhisperModel(modelSize, device="cpu", compute_type="int8")
            print(f"[ASR] Whisper model '{modelSize}' loaded successfully.")
        except Exception as e:
            print(f"[ASR] !!! Model loading failed: {e}")
            print("Please confirm faster-whisper and its dependencies (e.g., ctranslate2, ffmpeg) are installed.")
            self.model = None

    # —— Internal tools —— #
    def _do_transcribe(self, audioFile: str, language: Optional[str] = None) -> str:
        if self.model is None:
            print("[ASR] Error: Model is not loaded, cannot transcribe.")
            return ""
        if not Path(audioFile).exists():
            print(f"[ASR] Error: Audio file not found: {audioFile}")
            return ""

        start_time = time.time()
        try:
            # language=None → Automatic detection; otherwise, use the specified language.（"zh"/"en"/"ja"...）
            segments, info = self.model.transcribe(audioFile, language=language)
            text = "".join(seg.text for seg in segments).strip()
            duration = time.time() - start_time

            # During automatic detection, info.language can often provide the inference language.
            det_lang = getattr(info, "language", None)
            if language is None and det_lang:
                print(f"[ASR] Detected language: {det_lang}")

            print(f"[ASR] Recognition Result: {text}")
            print(f"[ASR] Recognition Time: {duration:.2f} seconds")
            return text
        except Exception as e:
            print(f"[ASR] !!! An error occurred during transcription: {e}")
            return ""

    # —— External main interface —— #
    def transcribe(self, audioFile: str) -> str:
        """
        Transcribes using the "configured language (ASR_LANGUAGE)" or auto-detection.
        - ASR_LANGUAGE = None  → Auto-detect (works for CH/EN)
        - ASR_LANGUAGE = "zh"  → Force Chinese
        - ASR_LANGUAGE = "en"  → Force English
        """
        try:
            language = ASR_LANGUAGE  # Could be None / "zh" / "en"
        except NameError:
            language = None  # If not defined, it will be automatically identified.
        return self._do_transcribe(audioFile, language=language)

    def transcribeAudio(self, audioFile: str, language: Optional[str] = None) -> str:
        """
        Alias method for compatibility with older control flows.
        - If 'language' is specified, it overrides the config.
        - If 'language'=None, it falls back to the configured language (same as self.transcribe).
        """
        if language is None:
            return self.transcribe(audioFile)
        return self._do_transcribe(audioFile, language=language)


# === independent test：python Voice/audio/whisperAsr.py ===
if __name__ == "__main__":
    print("--- WhisperAsr Module Standalone Test ---")
    data_dir = REPO_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    test_file = str(data_dir / "test_transcription.wav")

    # Record audio (if recording fails, place your wav in data/test_transcription.wav)
    print("\n[1/3] Recording for 3 seconds (if no mic, place file manually)...")
    fp = recordAudio(test_file, duration=3)

    if fp:
        print("\n[2/3] Initializing ASR ...")
        asr = WhisperAsr(modelSize=ASR_MODEL_SIZE)

        print("\n[3/3] Starting transcription (auto or configured lang)...")
        text = asr.transcribe(fp)
        print("\n--- Test Complete ---")
        print(f"Final Recognized Text: {text}")
    else:
        print("\nTest Failed: No audio file was obtained.")
