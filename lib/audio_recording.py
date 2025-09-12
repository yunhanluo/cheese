from threading import Thread
import pyaudio, wave

def record(path: str):
  p = pyaudio.PyAudio()

  chunk = 1024
  sampleFormat = pyaudio.paInt16
  channels = 2
  fs = 44100

  stream = p.open(
    format = sampleFormat, 
    channels = channels, 
    rate = fs,
    frames_per_buffer = chunk,
    input = True
  )

  frames = []

  waiting = True

  def callback():
    nonlocal waiting

    input()
    waiting = False

  Thread(target = callback).start()

  while waiting:
    data = stream.read(chunk)
    frames.append(data)

  stream.stop_stream()
  stream.close()
  p.terminate()

  wf = wave.open(f'sounds/{path}', 'wb')
  wf.setnchannels(channels)
  wf.setsampwidth(p.get_sample_size(sampleFormat))
  wf.setframerate(fs)
  wf.writeframes(b''.join(frames))
  wf.close()