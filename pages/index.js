const showhide = document.getElementById('showhidepassword');
const usernameIn = document.getElementById("username");
const passwordIn = document.getElementById('password');

var websocket;

function testKeyDown(event) {
  if (event == null) return;
  if (event.code == 'Enter' || event.code == 'Return') {
    document.getElementById('login').click();
  }
}

function login(type) {
  websocket = new WebSocket('ws://localhost:8001');

  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    if (event.type == 'success') {
      localStorage.setItem('196532ac-ae33-4e85-952a-e3a969fa70bc-collablens', JSON.stringify({
        'currentAccount': usernameIn.value
      }));
      window.location = `http://localhost:8000/home.html?username=${encodeURIComponent(usernameIn.value)}`;
    } else {
      document.getElementById('error').innerText = event.data;
    }
  });

  websocket.onopen = e => {
    websocket.send(JSON.stringify({
      'type': type,
      'username': usernameIn.value,
      'password': passwordIn.value
    }))
  };
}

showhide.onclick = e => {
  if (passwordIn.getAttribute('type') == 'password') {
    showhide.classList.remove('eyeOpen');
    showhide.classList.add('eyeClosed');
    passwordIn.setAttribute('type', 'text');
  } else {
    showhide.classList.remove('eyeClosed');
    showhide.classList.add('eyeOpen');
    passwordIn.setAttribute('type', 'password');
  }
};

{
  let data = localStorage.getItem('196532ac-ae33-4e85-952a-e3a969fa70bc-collablens');
  if (data != null) {
    data = JSON.parse(data);
    if (data.currentAccount.trim() != '') {
      window.location = `http://localhost:8000/home.html?username=${data.currentAccount}`;
    }
  }
}

document.getElementById('username').onkeydown = testKeyDown;
document.getElementById('password').onkeydown = testKeyDown;