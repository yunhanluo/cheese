from websockets.asyncio.server import serve
from random_name import generate_name
from typing import Any
import asyncio, secrets, json
import better_profanity as profanity
import speech_recognition as sr
import lib.ai_eval as ae
import lib.b64audio as b64audio

with open('pages/data/connection.json') as file:
  js: dict[str, str] = json.loads(file.read())
  HOST = js['ip']
  PORT = int(js['ws'])

with open('pages/data/accounts.json') as file:
  LOGINS: list[dict[str, Any]] = json.loads(file.read())['data']

async def error(websocket, msg):
  await websocket.send(json.dumps({
    'type': 'error',
    'data': msg,
    'sender': 'error'
  }))

async def runClient(websocket, key):
  print('user started with id ' + str(id(websocket)))
  myIndex = JOIN[key]['sockets'].index(websocket)
  async for message in websocket:
    data: dict[str, Any] = json.loads(message)
    match (data['type']):
      case 'message':
        if JOIN[key]['chainSpoken'][myIndex] == 3:
          await error(websocket, 'you\'ve spoken a lot, let someone else speak first!')
          continue
        msg = prof.censor(data['data'])
        JOIN_LOG[key]['chat'] += str(id(websocket)) + ': ' + msg
        JOIN[key]['chainSpoken'][myIndex] += 1
        if msg != data['data']:
          deduction = msg.count('****')
          await error(websocket, f'please do not cuss. -{deduction} {"pt" if deduction == 1 else "pts"}')
          JOIN[key]['points'][myIndex] -= deduction
          JOIN[key]['ptshistory'][myIndex].append(JOIN[key]['points'][myIndex])
        for connection in JOIN[key]['sockets']:
          await connection.send(json.dumps({
            'type': 'message',
            'data': msg,
            'sender': id(websocket),
            'senderreal': JOIN_UQ[key]['names'][id(websocket)],
            'points': JOIN[key]['points'][myIndex],
            'badges': JOIN[key]['badges'][myIndex]
          }))
          if connection != websocket:
            await connection.send(json.dumps({
              'type': 'resetSpoken',
              'data': '',
              'sender': id(websocket),
              'senderreal': JOIN_UQ[key]['names'][id(websocket)]
            }))
      case 'audio':
        if JOIN[key]['chainSpoken'][myIndex] == 3:
          await error(websocket, 'you\'ve spoken a lot, let someone else speak first!')
          continue

        # b64audio.b64toWav(data['data'], 'sounds/bite.wav')
        b64audio.b64toWav(data['data'], 'sounds')
        # b64audio.b64toWav(data['data'], 'sounds/bite.wav', 1, 2, 44100)
        msgold = json.loads(recog.recognize_vosk(sr.AudioData.from_file('sounds/output.wav')))['text']
        msg = prof.censor(msgold)

        JOIN_LOG[key]['chat'] += str(id(websocket)) + ': ' + msg
        JOIN[key]['chainSpoken'][myIndex] += 1

        if msg != msgold:
          deduction = msg.count('****')
          await error(websocket, f'please do not cuss. -{deduction} {"pt" if deduction == 1 else "pts"}')
          JOIN[key]['points'][myIndex] -= deduction
          JOIN[key]['ptshistory'][myIndex].append(JOIN[key]['points'][myIndex])

        for connection in JOIN[key]['sockets']:
          await connection.send(json.dumps({
            'type': 'audio',
            'data': data['data'],
            'sender': id(websocket),
            'senderreal': JOIN_UQ[key]['names'][id(websocket)],
            'points': JOIN[key]['points'][myIndex],
            'badges': JOIN[key]['badges'][myIndex],
            'transcription': msg
          }))
      case 'process':
        chatlog = []
        for line in JOIN_LOG[key]['chat'].strip().split('\n'):
          ld = line.split(': ', 1)
          if len(ld) < 2: continue
          if ld[1] == 'connected' or ld[1] == 'disconnected' or not ld[0].isdigit(): continue
          chatlog.append({
            'sender': int(ld[0]),
            'data': ld[1]
          })
        results = json.loads(await ae.eval_text_points(chatlog, "conversation_prompt"))['messages'] # type: ignore
        for thing in results:
          for i in range(len(JOIN[key]['sockets'])):
            connection = JOIN[key]['sockets'][i]
            if id(connection) == int(thing["sender"]):
              pts = int(thing["points"])
              if pts < 0:
                await connection.send(json.dumps({
                  'type': 'message',
                  'data': f'You have been deducted {-pts} {"pt" if abs(pts) == 1 else "pts"} for this reason: {thing["reasoning"]}',
                  'sender': 'ai',
                  'senderreal': 'ai'
                }))
              elif pts > 0:
                await connection.send(json.dumps({
                  'type': 'message',
                  'data': f'You have been added {pts} {"pt" if pts == 1 else "pts"} for this reason: {thing["reasoning"]}',
                  'sender': 'ai',
                  'senderreal': 'ai'
                }))
              JOIN[key]['points'][i] += pts
              JOIN[key]['ptshistory'][i].append(JOIN[key]['points'][i])
              break
        
        results = json.loads(await ae.eval_text_points(chatlog, "response_prompt")) # type: ignore
        if results['priority'] > 5:
          for connection in JOIN[key]['sockets']:
            await connection.send(json.dumps({
              'type': 'message',
              'data': results['data'],
              'sender': 'ai',
              'senderreal': 'ai'
            }))
      case 'resetSpoken':
        JOIN[key]['chainSpoken'][myIndex] = 0
      case 'badge':
        try:
          uid = list(JOIN_UQ[key]['names'].keys())[list(JOIN_UQ[key]['names'].values()).index(data['data'])]
          for i in range(len(JOIN[key]['sockets'])):
            connection = JOIN[key]['sockets'][i]
            if id(connection) == uid:
              await connection.send(json.dumps({
                'type': 'badge',
                'data': data['reason'],
                'sender': data['sender'],
                'senderreal': JOIN_UQ[key]['names'][int(data['sender'])]
              }))
              JOIN[key]['badges'][i].append(str(data['sender']) + ': ' + str(data['reason']))
              break
        except (KeyError, ValueError, TypeError):
          pass
      case 'ppath':
        sending: dict[str, Any] = {'type': 'ppath'}
        mLen = 0
        for i in range(min(len(JOIN[key]['sockets']), 2)):
          sending[f'd{"One" if i == 1 else "Two"}'] = JOIN[key]['ptshistory'][i]
          sending[f'u{"One" if i == 1 else "Two"}'] = JOIN_UQ[key]['names'][id(JOIN[key]['sockets'][i])]
          if len(JOIN[key]['ptshistory'][i]) > mLen:
            mLen = len(JOIN[key]['ptshistory'][i])
        sending['len'] = mLen
        for connection in JOIN[key]['sockets']:
          await connection.send(json.dumps(sending))
          

async def start(websocket, us):
  key = secrets.token_urlsafe(12)
  JOIN[key] = {"sockets": [websocket], "chainSpoken": [0], "points": [0], "badges": [[]], "ptshistory": [[0]]}
  JOIN_UQ[key] = {"names": {id(websocket): us}}
  JOIN_LOG[key] = {'chat': ''}

  print('user started server with key ' + key)

  try:
    await websocket.send(json.dumps({
      'type': 'init',
      'data': key,
      'sender': id(websocket),
      'senderreal': JOIN_UQ[key]['names'][id(websocket)],
      'points': JOIN[key]['points'][0],
      'started': 'yes',
      'ip': HOST
    }))

    await runClient(websocket, key)
  finally:
    del JOIN[key]
    print('user ' + str(id(websocket)) + ' disconnected, stopping server ' + key)

async def join(websocket, ev):
  key = ev['data']
  try:
    connected = JOIN[key]['sockets']
    JOIN[key]['chainSpoken'].append(0)
    JOIN[key]['points'].append(0)
    JOIN[key]['badges'].append([])
    JOIN[key]['ptshistory'].append([0])
    JOIN_UQ[key]['names'][id(websocket)] = ev['username']
    myIndex = len(connected) - 1
  except KeyError:
    await error(websocket, 'server not found.')
    return
  
  connected.append(websocket)
  print('user connected on key ' + key)

  try:
    await websocket.send(json.dumps({
      'type': 'init',
      'data': key,
      'sender': id(websocket),
      'senderreal': JOIN_UQ[key]['names'][id(websocket)],
      'points': JOIN[key]['points'][myIndex],
      'started': 'no',
      'ip': HOST
    }))
    for socket in connected:
      if socket == websocket:
        continue
      await socket.send(json.dumps({
        'type': 'message',
        'data': 'connected',
        'sender': id(websocket),
        'senderreal': JOIN_UQ[key]['names'][id(websocket)],
        'points': JOIN[key]['points'][myIndex]
      }))

    await runClient(websocket, key)
  finally:
    for socket in connected:
      if socket == websocket:
        continue
      await socket.send(json.dumps({
        'type': 'message',
        'data': 'disconnected',
        'sender': id(websocket),
        'senderreal': JOIN_UQ[key]['names'][id(websocket)],
      }))
    connected.remove(websocket)
    print('user ' + str(id(websocket)) + ' disconnected')

async def verify(websocket, ev):
  status = 0
  for login in LOGINS:
    if login['username'] == ev['username']:
      if login['password'] == ev['password']:
        await websocket.send(json.dumps({
          'type': 'success'
        }))
        return
      status = 1
  if status == 0:
    await error(websocket, 'Incorrect username.')
  else:
    await error(websocket, 'Incorrect password.')
      
async def register(websocket, ev):
  global LOGINS

  for login in LOGINS:
    if login['username'] == ev['username']:
      await error(websocket, 'This username has already been taken.')
      return
  with open('pages/data/accounts.json', 'w') as file:
    LOGINS.append({
      'username': ev['username'],
      'password': ev['password']
    })
    file.write(json.dumps({"data": LOGINS}))

    await websocket.send(json.dumps({'type': 'success'}))

async def handler(websocket):
  try:
    msg = await websocket.recv()
    event = json.loads(msg)

    match (event["type"]):
      case "join":
        await join(websocket, event)
      case "init":
        await start(websocket, event['username'])
      case "verifyLogin":
        await verify(websocket, event)
        await websocket.close(code=1000, reason="closed")
      case "register":
        await register(websocket, event)
        await websocket.close(code=1000, reason="closed")
      case _:
        await error(websocket, 'invalid type as first send: ' + event["type"])
  except Exception as e:
    print(e)

async def main():
  async with serve(handler, HOST, PORT) as server:
    print(f'running server on {HOST}:{PORT}')
    await server.serve_forever()

JOIN: dict[str, dict[str, list]] = {}
JOIN_UQ: dict[str, dict[str, dict[int, Any]]] = {}
JOIN_LOG: dict[str, dict[str, str]] = {}
prof = profanity.Profanity()
recog = sr.Recognizer()

if __name__ == "__main__":
  print('----------\nVosk: ' + recog.recognize_vosk(sr.AudioData.from_file('sounds\\boot.wav')))


  asyncio.run(main())
