const messages = document.querySelector('div#messages')
const input = document.querySelector('input#input');
const websocket = new WebSocket("ws://127.0.0.1:8001/");
var chat = '';
var myId;
var recorder, audioChunks, recording;

function add(message, sender, sp) {
  let e = document.createElement('p');
  e.innerHTML = '<span>' + sender + (sp != null ? sp : '') + ':</span><span>' + message + '</span>';
  e.classList.add('message');
  if (sender == myId) e.classList.add('self');
  else if (sender == 'error') e.classList.add('error');
  else e.classList.add('other');
  messages.appendChild(e);
  if (sender != 'error') chat += sender + ': ' + message + '\n';
}
function addAudio(data, sender) {
  let e = document.createElement('p');
  let aud = document.createElement('audio');
  aud.controls = true;
  aud.src = data;
  e.innerHTML = '<span>' + sender + (sp != null ? sp : '') + ':';
  e.appendChild(aud);
  e.innerHTML += '</span>';
  if (sender == myId) e.classList.add('self');
  else if (sender == 'error') e.classList.add('error');
  else e.classList.add('other');

  messages.appendChild(e);
  chat += sender + ': ' + 'audio file' + '\n';
}

function sendText() {
  let message = input.value;
  if (input.value == '') return;
  input.value = '';
  try {
    websocket.send(JSON.stringify({
      'data': message,
      'type': 'message'
    }));
  } catch (e) {
    if (e.message.includes("Still in CONNECTING state")) {
      add('WebSocket error: The client has not connected!', 'error');
    }
  }
}
function sendAudio(audioUrl) {
  try {
    websocket.send(JSON.stringify({
      'data': audioUrl,
      'type': 'audio'
    }));
  } catch (e) {
    if (e.message.includes("Still in CONNECTING state")) {
      add('WebSocket error: The client has not connected!', 'error');
    }
  }
}

function saveChat() {
  let element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(chat));
  element.setAttribute('download', 'chat.txt');

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function awardPoints() {
  let chatData = [];
  for (const string of chat.split('\n')) {
    data = string.split(': ');
    chatData.push({
      'user_id': data[0],
      'text': data[1]
    });
  }

  websocket.send(JSON.stringify({
    'type': 'process',
    'data': JSON.stringify({
      'role': 'user',
      'content': chatData
    })
  }));
}
function awardBadge() {
  websocket.send(JSON.stringify({
    'type': 'badge',
    'data': alert('enter the user ID you want to award the badge to')
  }));
}

async function toggleRecording() {
  try {
    if (recording) {
      recorder.stop();
      recording = false;
      document.querySelector('button#record').innerHTML = '<span>&#x2b24;</span>';
    } else {
      if (recorder == null) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);
        recorder.ondataavailable = event => {
          audioChunks.push(event.data);
        };
        recorder.onstop = event => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          const audioUrl = URL.createObjectURL(audioBlob);
          sendAudio(audioUrl);
        };
      }
      document.querySelector('button#record').innerHTML = '<span>&#x23f9;</span>';
      audioChunks = [];
      recorder.start();
      recording = true;
    }
  } catch (e) {
    add('Microphone error: ' + e, "error");
  }
}
async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch {}
}

websocket.addEventListener("message", ({ data }) => {
  const event = JSON.parse(data);
  let sender, senderPlus;
  switch (event.type) {
    case 'message':
      sender = event.sender;
      senderPlus = '';
      if ("points" in event) {
        senderPlus += ', ' + event.points + (parseInt(event.points) == 1 ? ' pt' : ' pts');
      } if ("badges" in event) {
        if (! senderPlus.includes(', ')) senderPlus += ', ';
        senderPlus += '<span class="badge"></span>'.repeat(parseInt(event.badges));
      }
      add(event.data, sender, senderPlus);
      break;
    case 'badge':
      add('you have been awarded a kindness badge!', 'console', '')
    case 'resetSpoken':
      websocket.send(JSON.stringify(event));
      break;
    case 'audio':
      sender = event.sender;
      senderPlus = '';
      if ("points" in event) {
        senderPlus += ', ' + event.points + (parseInt(event.points) == 1 ? ' pt' : ' pts');
      } if ("badges" in event) {
        if (! senderPlus.includes(', ')) senderPlus += ', ';
        senderPlus += '<sp'
      }
      addAudio(event.data, sender, senderPlus);
      break;
    case 'close':
      websocket.close(1000);
      break;
    case 'init':
      let actions = document.querySelector('div#actions');

      myId = event.sender;
      let e = document.createElement('p');
      e.innerText = 'Your user ID: ' + myId;
      actions.appendChild(e);

      e = document.createElement('a');
      e.href = 'http://192.168.8.50:8000/?join=' + event.data;
      e.innerText = "Join Link";
      e.target = "_blank";
      actions.appendChild(e);

      e = document.createElement('a');
      e.href = 'javascript:copy(\"http://192.168.8.50:8000/?join=' + event.data + '\");';
      e.innerText = "Copy Link";
      e.target = "";
      actions.appendChild(e);

      e = document.createElement('a');
      e.href = 'javascript:saveChat();';
      e.innerText = "Save Chat";
      e.target = "";
      actions.appendChild(e);

      e = document.createElement('a');
      e.href = 'javascript:awardBadge();';
      e.innerText = "Award Kindness Badge";
      e.target = "";
      actions.appendChild(e);

      if (event.started == 'yes') {
        e = document.createElement('a');
        e.href = 'javascript:awardPoints();';
        e.innerText = "Award Kindness Points";
        e.target = "";
        actions.appendChild(e);
      }
      break;
    case 'error':
      add(event.data, 'error');
      break;
    default:
      throw new Error(`Unsupported event type: ${event.type}.`);
  }
});
websocket.addEventListener("open", () => {
  const params = new URLSearchParams(window.location.search);
  let event = {};
  if (params.has("join")) {
    event.type = 'join';
    event.data = params.get("join");
    console.log(event.data);
  } else {
    event.type = 'init';
    event.data = 8000;
  }
  websocket.send(JSON.stringify(event));
});
websocket.addEventListener("error", () => {
  add('WebSocket error: The client failed to connect.', 'error');
});

document.querySelector('button#submit').onclick = e => {
  sendText();
};
document.querySelector('button#record').onclick = e => {
  toggleRecording();
};
document.querySelector('div#textarea').onkeydown = e => {
  if (e.code == 'Enter' || e.code == 'Return') {
    sendText();
  }
};

add('testing', 'tester', ', <span class="badge"></span>')
add('testing', 'tester', ', <span class="badge"></span><span class="badge"></span>')