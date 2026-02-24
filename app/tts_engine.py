import os
import tempfile
from pathlib import Path
from datetime import datetime


def shift_pitch(input_path: str, output_path: str, semitones: float) -> bool:
    """
    Shift pitch of an audio file by N semitones.
    Returns True if successful, False if pydub not available.
    """
    if abs(semitones) < 0.1:
        import shutil
        shutil.copy2(input_path, output_path)
        return True

    try:
        from pydub import AudioSegment

        sound = AudioSegment.from_file(input_path)
        factor = 2 ** (semitones / 12.0)
        new_sample_rate = int(sound.frame_rate * factor)

        pitched = sound._spawn(sound.raw_data, overrides={"frame_rate": new_sample_rate})
        pitched = pitched.set_frame_rate(sound.frame_rate)  # Reset to original rate

        fmt = "mp3" if output_path.endswith(".mp3") else "wav"
        try:
            pitched.export(output_path, format=fmt)
        except Exception:
            pitched.export(output_path, format="wav")

        return True

    except ImportError:
        import shutil
        shutil.copy2(input_path, output_path)
        return False
    except Exception as e:
        print(f"Pitch shift failed: {e}")
        import shutil
        shutil.copy2(input_path, output_path)
        return False


def speak_pyttsx3(text: str, params: dict, output_path: str) -> bool:
    """
    Generate speech using pyttsx3 with custom rate and volume.
    Returns True on success.
    """
    try:
        import pyttsx3

        engine = pyttsx3.init()

        engine.setProperty("rate", params["rate"])

        engine.setProperty("volume", params["volume"])

        temp_wav = output_path.replace(".mp3", ".wav")
        if not temp_wav.endswith(".wav"):
            temp_wav = output_path + ".wav"

        engine.save_to_file(text, temp_wav)
        engine.runAndWait()

        print(f"  [pyttsx3] Rate: {params['rate']} wpm | Volume: {params['volume']}")

        pitch = params.get("pitch", 0)
        if abs(pitch) > 0.1:
            print(f"  [pyttsx3] Applying pitch shift: {pitch:+.1f} semitones")
            pitched_path = output_path if output_path.endswith((".wav", ".mp3")) else output_path + ".wav"
            success = shift_pitch(temp_wav, pitched_path, pitch)
            if success and pitched_path != temp_wav:
                os.remove(temp_wav)
        else:
            if temp_wav != output_path:
                import shutil
                shutil.move(temp_wav, output_path)

        return os.path.exists(output_path) and os.path.getsize(output_path) > 0

    except ImportError:
        print("  [pyttsx3] Not installed. Trying gTTS...")
        return False
    except Exception as e:
        print(f"  [pyttsx3] Error: {e}")
        return False

def speak_gtts(text: str, params: dict, output_path: str) -> bool:
    """
    Generate speech using gTTS (Google Text-to-Speech).
    Returns True on success.
    """
    try:
        from gtts import gTTS

        use_slow = params["rate"] < 150

        tts = gTTS(text=text, lang="en", slow=use_slow)
        temp_mp3 = output_path.replace(".wav", ".mp3")
        if not temp_mp3.endswith(".mp3"):
            temp_mp3 = output_path + ".mp3"

        tts.save(temp_mp3)
        print(f"  [gTTS] Slow mode: {use_slow} (rate target: {params['rate']} wpm)")

        pitch = params.get("pitch", 0)
        final_path = output_path if output_path.endswith((".mp3", ".wav")) else temp_mp3

        if abs(pitch) > 0.1:
            print(f"  [gTTS] Applying pitch shift: {pitch:+.1f} semitones")
            shift_pitch(temp_mp3, final_path, pitch)
            if final_path != temp_mp3 and os.path.exists(temp_mp3):
                os.remove(temp_mp3)
        elif temp_mp3 != final_path:
            import shutil
            shutil.move(temp_mp3, final_path)

        return os.path.exists(final_path) and os.path.getsize(final_path) > 0

    except ImportError:
        print("  [gTTS] Not installed. pip install gTTS")
        return False
    except Exception as e:
        print(f"  [gTTS] Error: {e}")
        return False

def generate_speech(text: str, params: dict, output_dir: str = "output") -> str:
    """
    Tries pyttsx3 first (offline), falls back to gTTS (online).

    Args:
        text:       The text to convert to speech
        params:     Voice parameters from mapping.py (rate, volume, pitch)
        output_dir: Directory where audio file will be saved
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"empathy_output_{timestamp}.wav")

    print(f"  Target output: {output_path}")

    success = speak_pyttsx3(text, params, output_path)

    if not success:
        print("  Falling back to gTTS...")
        mp3_path = output_path.replace(".wav", ".mp3")
        success = speak_gtts(text, params, mp3_path)
        if success:
            output_path = mp3_path

    if success:
        size_kb = os.path.getsize(output_path) / 1024
        print(f"Audio saved: {output_path} ({size_kb:.1f} KB)")
        return output_path
    else:
        print("TTS engines failed. Check your installation.")
        return ""


if __name__ == "__main__":
    params = {"rate": 175, "volume": 0.9, "pitch": 0, "pause_factor": 1.0}
    result = generate_speech("Hello, this is a test of the empathy engine.", params, "output")
    print(f"Result: {result}")
