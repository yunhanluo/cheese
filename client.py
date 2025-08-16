from random_name import generate_name
from speech_recognition import Recognizer
from threading import Thread
from time import time
import better_profanity as prof
import lib.audio_recording as audio
import lib.audio_recognition as sr
import socket, json

def recv(sock: socket.socket):
  global spokenChain
  while True:
    try:
      res = sock.recv(1024)
    except ConnectionResetError:
      msg('console', 'server disconnected')
      exit()
      return
    
    data = res.decode()

    match (data[0]):
      case 'a':
        rec = data[1:].split('&')
        msg(rec[0], rec[1])
        spokenChain = 0
        continue
      case _:
        continue
def println(string: str):
  global chatHistory

  print(string)
  chatHistory += ('' if chatHistory == '' else '\n') + string
  with open('data\\data.json', 'w') as file:
    json.dump({
      "chatHistory": chatHistory
    }, file)
def reloadChat():
  print(chatHistory)
def msg(sender: str, message: str):
  colorCode = '\x1b[0m'
  if sender == 'console':
    colorCode = '\x1b[33m'
  elif sender == 'error':
    colorCode = '\x1b[31m'
    sender = 'console'
  println(colorCode + sender + ': ' + message.strip() + '\x1b[0m')
def send(message: str):
  global spokenChain
  spokenChain += 1
  filtered = profanity.censor(message.replace('&', ''))
  client.send(f'a{filtered}'.encode())
  msg('you', filtered)
  if '&' in message:
    msg('error', 'you sent &, which is an illegal character.')
  elif profanity.contains_profanity(message):
    msg('error', 'no cussing')
def showRec():
  while recording:
    reloadChat()
    print('\x1b[3A\x1b[1000D\x1b[80C\x1b[31mRECORDING\x1b[0m\x1b[3B\x1b[1000C')

    if not recording: break
    preTime = time()
    while time() - preTime < .5:
      if not recording: return

    reloadChat()

    if not recording: break
    preTime = time()
    while time() - preTime < .5:
      if not recording: return

ip = input('Enter the server IP: ')
if ip.strip() == '':
  ip = '127.0.0.1'

port = int(input('Enter the port: '))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ip, port))

name = generate_name()
client.send(name.encode())

chatHistory = ""
recording = False
spokenChain = 0
profanity = prof.Profanity()



r = Recognizer()
val = sr.recognize(r, 'boot.wav')
println(f'\x1b[2J\x1b[1000A\x1b[1000D\x1b[0;1mCollabLens\n{"-" * 20}\x1b[0m\n')
if len(val.strip()) > 0:
  msg('console', 'vosk initialized')
else:
  msg('error', 'vosk failed to initialize. voice recording may not work.')

recvThread = Thread(target = recv, args = [client])
recvThread.start()

while True:
  val = input()
  if val.lower() == '/stop':
    exit()
  else:
    if spokenChain > 2:
      reloadChat()
      msg('error', 'you spoke too many times, let someone else speak first!')
    elif len(val.strip()) != 0:
      send(val)
      reloadChat()
    else:
      recording = True
      Thread(target = showRec).start()
      audio.record('bite.wav')
      recording = False
      send(sr.recognize(r, "bite.wav"))
      reloadChat()