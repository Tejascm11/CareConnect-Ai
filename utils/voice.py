import tempfile
import speech_recognition as sr
from gtts import gTTS

# ---------------- VOICE INPUT ----------------
def listen_from_mic(language="en-US"):
    """
    Converts microphone speech to text.
    Returns None if speech is not understood.
    """
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source)

        text = recognizer.recognize_google(audio, language=language)
        return text

    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None
    except Exception:
        return None


# ---------------- VOICE OUTPUT ----------------
def speak_text(text, lang="kn"):
    """
    Converts text to speech and returns audio file path.
    Default language: Kannada (kn)
    """
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception:
        return None
