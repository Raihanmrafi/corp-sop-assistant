import speech_recognition as sr
from gtts import gTTS
import os

def record_voice():
    """Merekam suara dari microphone dan mengubahnya jadi teks."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Mendengarkan...") # Log ke terminal
        audio = r.listen(source, timeout=5, phrase_time_limit=10)
        try:
            text = r.recognize_google(audio, language="id-ID")
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return "Error koneksi Google Speech"

def text_to_speech_file(text):
    """Mengubah teks jadi file audio MP3."""
    try:
        tts = gTTS(text=text, lang='id')
        filename = "answer.mp3"
        # Hapus file lama jika ada agar tidak konflik
        if os.path.exists(filename):
            os.remove(filename)
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Error TTS: {e}")
        return None