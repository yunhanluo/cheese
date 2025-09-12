import better_profanity as prof
import speech_recognition as sr
from vosk import SetLogLevel
import json # , socket

def recognize(r: sr.Recognizer, path) -> str:
  with sr.AudioFile(f'sounds/{path}') as source:
    try:
      recognized = r.recognize_vosk(r.record(source))
    except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
      return ''
    else:
      pr = prof.Profanity()
      text: str = json.loads(recognized)['text']
      if len(text.strip()) == 0:
        return ''
      elif pr.contains_profanity(text):
        return '\x1b[31m' + pr.censor(text) + '\x1b[0m'
      else:
        return '\x1b[0m' + text

# SetLogLevel(-1)
# print(recognize(sr.Recognizer(), 'boot.wav'))