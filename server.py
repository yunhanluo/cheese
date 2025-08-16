from threading import Thread
import socket, time

def handleClient(sock: socket.socket, addr):
  activeSockets.append(sock)

  name = sock.recv(1024).decode()

  # print(f'{addr} connected with name {name}')

  while True:
    try:
      data = sock.recv(1024)
    except (ConnectionResetError, OSError):
      return
    
    if not data:
      # print(f'{name} disconnected')
      for asock in activeSockets:
        if asock == sock:
          continue
        try:
          asock.send(f'a{name} disconnected'.encode())
        except OSError:
          pass
      if input('kill server? [y/N]').lower().strip() == 'y':
        for asock in activeSockets:
          asock.close()
        server.close()
        exit()
      break

    data = data.decode()
    
    if data.strip() == '':
      continue

    # print(f'recieved {data[1:]} from {name}')

    match (data[0]):
      case 'a':
        for asock in activeSockets:
          if asock == sock:
            continue
          try:
            if anonymous:
              asock.send(f'asomeone&{data[1:]}'.encode())
            else:
              asock.send(f'a{name}&{data[1:]}'.encode())
          except OSError:
            # print(f'failed to send \"{data[1:]}\" to {name}')
            pass
        continue
      case _:
        # print(f'recieved unknown control character {data[0]} from {name}')
        continue
  
  sock.close()
def inputThread():
  global anonymous
  while True:
    val = input('> ')
    match val:
      case 'stop':
        # print("\nkilling server...")
        exit()
        return
      case 'hide':
        anonymous = True
        continue

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = input('Enter the server IP: ')
if len(ip.strip()) == 0:
  ip = '127.0.0.1'

port = 1
preTime = time.time_ns()
while True:
  try:
    server.bind((ip, port))
  except OSError as e:
    if 'Can\'t assign requested address' in str(e):
      print(f'could not assign to address {ip}')
      time.sleep(1.5)
      exit()
    port += 1
    if port > 65535:
      print('could not find an available port.')
      time.sleep(1.5)
      exit()
  else:
    break
print(f'server connected on address {ip} and port {port} in {time.time_ns() - preTime} ns')

activeSockets: list[socket.socket] = []
sockThreads: list[Thread] = []

anonymous = False

print('listening for 4 users...')
server.listen(4)

Thread(target = inputThread).start()

while True:
  try:
    client, client_address = server.accept()
    sockThreads.append(Thread(target = handleClient, args = (client, client_address)))
    sockThreads[-1].start()
  except (ConnectionAbortedError, AssertionError):
    pass
  except OSError as e:
    print(e)
    break