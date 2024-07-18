
import io

import speech_recognition as sr
from pydub import AudioSegment

class RecognizedText:
    def __init__(self, text=None, error=None):
        self.text = text
        self.error = error

def convertAudio2Waw(bytes):
    wavBytes = io.BytesIO()
    bytes.export(wavBytes, format='wav')
    wavBytes.seek(0)
    return wavBytes

def recognizeTextByAudio(audioData):
    oggBytes = AudioSegment.from_file(audioData, format='ogg')
    wavBytes = convertAudio2Waw(oggBytes)
    rec = sr.Recognizer()
    with sr.AudioFile(wavBytes) as source:
        audio = rec.record(source)
    text, error = None, None
    try: text = rec.recognize_google(audio, language='ru-RU')
    except sr.UnknownValueError: error = 'Не удалось распознать речь'
    except sr.RequestError as err: error = err
    finally: recognizedText = RecognizedText(text, error)
    return recognizedText

