# audio/recordAudio.py
import pyaudio
import wave
import os

# --- Workaround to add project root to sys.path for independent execution ---
# We need to add the project root (smart-home-voice) to sys.path
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))
# --- End of path workaround ---

try:
    from config.settings import RECORD_DURATION
except ImportError:
    print("Warning: config.settings not found. Using default RECORD_DURATION=4")
    RECORD_DURATION = 4


def recordAudio(filename: str = "input.wav", duration: int = RECORD_DURATION) -> str:
    """
    Records audio for a specified duration and saves it to a file.

    Args:
        filename (str): The file path to save the audio. Defaults to "input.wav".
        duration (int): The recording duration in seconds. Defaults to RECORD_DURATION from settings.

    Returns:
        str: The file path where the audio was saved upon success, or None on failure.
    """
    chunk = 1024
    sampleFormat = pyaudio.paInt16
    channels = 1
    fs = 16000  # 16kHz sampling rate, suitable for speech recognition

    p = pyaudio.PyAudio()

    print(f"🎤 Recording... Please speak ({duration} seconds)")

    try:
        stream = p.open(format=sampleFormat, channels=channels,
                        rate=fs, frames_per_buffer=chunk, input=True)
    except IOError as e:
        print(f"!!! Could not open microphone. Please check device and permissions. Error: {e}")
        p.terminate()
        return None  # Return None to indicate failure

    frames = []
    try:
        for _ in range(int(fs / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
    except IOError as e:
        print(f"!!! Error occurred during recording: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sampleFormat))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"✅ Recording saved: {filename}")
    return filename


# --- Independent Test Module ---
if __name__ == "__main__":
    # This code executes when you run `python audio/recordAudio.py` directly
    print("--- Testing recordAudio Module ---")

    # Ensure data directory exists (based on project structure)
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    test_file_path = str(data_dir / "test_recording.wav")

    print(f"Will record 3 seconds of audio to: {test_file_path}")
    file_path = recordAudio(test_file_path, duration=3)  # Test recording for 3 seconds

    if file_path:
        print(f"\nTest Successful!")
        print(f"File path: {file_path}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
        print("You can play data/test_recording.wav to check the recording.")
    else:
        print("\nTest Failed.")
