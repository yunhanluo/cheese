const messages = document.querySelector('div#messages')
const input = document.querySelector('input#input');
const websocket = new WebSocket("ws://192.168.8.65:8001/");
var chat = '';
var savedchat = '';
var myId;
var IP;
var recorder, audioChunks, recording;
var pdata = [];

function add(message, sender, sp) {
  let e = document.createElement('p');
  e.innerHTML = '<span>' + sender + (sp != null ? sp : '') + ':</span><span>' + message + '</span>';
  e.classList.add('message');
  if (sender == myId) e.classList.add('self');
  else if (sender == 'error') e.classList.add('error');
  else e.classList.add('other');
  messages.appendChild(e);
  if (sender != 'error') {
    chat += sender + ': ' + message + '\n';
    savedchat += sender + ': ' + message + '\n';
  }
}
function addAudio(data, sender) {
  let e = document.createElement('p');
  let aud = document.createElement('audio');
  aud.controls = true;
  aud.src = data;
  e.innerHTML = '<span>' + sender + ':</span>';
  e.appendChild(aud);
  e.classList.add('message');
  e.classList.add('hasaudio');
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
  websocket.send(JSON.stringify({
    'type': 'process',
    'data': savedchat
  }));
  savedchat = '';
}
function awardBadge() {
  let uid = window.prompt('enter the user ID you want to award the badge to');
  if (uid == myId || uid == null || uid == undefined) {
    alert('You can\'t give yourself a kindness badge!');
    return;
  }

  let action = window.prompt('what did they do to deserve a badge?');
  if (action == null || action == undefined || action.trim() == '') {
    alert('Please provide a reason.');
    return;
  }

  websocket.send(JSON.stringify({
    'type': 'badge',
    'data': uid,
    'reason': action,
    'sender': myId
  }));
}

function chartPoints() {
  websocket.send(JSON.stringify({
    'type': 'ppath'
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
        for (const badge of event.badges) {
          senderPlus += `<span class="badge icon"><span class=\"tooltiptext\">${badge}</span></span>`;
        }
      }
      add(event.data, sender, senderPlus);
      break;
    case 'badge':
      add(`you have been awarded a kindness badge by ${event.sender}! their reason: ${event.data}`, 'console', '')
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
        for (const badge in event.badges) {
          senderPlus += `<span class="badge icon"><span class=\"tooltiptext\">${badge}</span></span>`;
        }
      }
      addAudio(event.data, sender, senderPlus);
      break;
    case 'close':
      websocket.close(1000);
      break;
    case 'init':
      let actions = document.querySelector('div#actions');

      IP = event.ip;

      myId = event.sender;
      let e = document.createElement('p');
      e.innerText = 'Your user ID: ' + myId;
      actions.appendChild(e);

      e = document.createElement('a');
      e.href = `http://${IP}:8000/?join=` + event.data;
      e.innerHTML = "<span class=\"icon link\"></span>Join Link";
      e.target = "_blank";
      actions.appendChild(e);

      e = document.createElement('a');
      e.href = `javascript:copy(\"http://${IP}:8000/?join=${event.data}\");`;
      e.innerHTML = "<span class=\"icon link\"></span>Copy Link";
      e.target = "";
      actions.appendChild(e);

      e = document.createElement('a');
      e.href = 'javascript:saveChat();';
      e.innerHTML = "<span class=\"icon download\"></span>Save Chat";
      e.target = "";
      actions.appendChild(e);

      e = document.createElement('a');
      e.href = 'javascript:awardBadge();';
      e.innerHTML = "<span class=\"icon badge\"></span>Award Kindness Badge";
      e.target = "";
      actions.appendChild(e);

      if (event.started == 'yes') {
        e = document.createElement('a');
        e.href = 'javascript:awardPoints();';
        e.innerHTML = "<span class=\"icon ai\"></span>Award Kindness Points";
        e.target = "";
        actions.appendChild(e);

        e = document.createElement('a');
        e.href = 'javascript:chartPoints();';
        e.innerHTML = "<span class=\"icon chart\"></span>Display Points Chart";
        e.target = "";
        actions.appendChild(e);
      }
      break;
    case 'error':
      add(event.data, 'error');
      break;
    case 'ppath':
      for (const ele in document.querySelectorAll('span:has(canvas#myChart)')) {
        if (ele instanceof Element) ele.remove();
      }

      let e2 = document.createElement('canvas');
      e2.id = 'myChart';
      e2.style.width = '100%';
      e2.style.maxWidth = '600px';

      let e3 = document.createElement('p');
      e3.appendChild(e2);

      messages.appendChild(e3);
      
      new Chart("myChart", {
        type: "line",
        data: {
          labels: Array.from({ length: parseInt(event.len) }, (_, i) => i + 1),
          datasets: [{ 
            data: event.dOne,
            borderColor: "red",
            fill: false,
            label: event.uOne
          }, { 
            data: event.dTwo,
            borderColor: "green",
            fill: false,
            label: event.uTwo
          }]
        },
        options: {
          legend: {
            display: true
          },
          plugins: {
            title: {
              display: true,
              text: 'Kindness Points'
            }
          }
        }
      });

      websocket.close();
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
    // console.log(event.data);
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

// add('testing', 'tester', '<span class=\"badge\"><span class=\"tooltiptext\">Kindness badge</span></span>')
// add('testing 2', 'tester 2', '<span class=\"badge\"><span class=\"tooltiptext\">Kindness badge</span></span><span class=\"badge\"><span class=\"tooltiptext\">Kindness badge</span></span>')