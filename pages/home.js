{
  const params = new URLSearchParams(window.location.search);
  var username = decodeURIComponent(params.get('username'));
  document.getElementById('usn').innerText = `Welcome, ${username}`;
}

function goToMeeting() {
  const val = document.getElementById('mid').value;
  if (encodeURIComponent(val) != val) {
    return;
  }
  let e = document.createElement('a');
  e.href = `http://localhost:8000/chat.html?join=${val}&username=${username}`;
  e.target = '_blank';
  document.body.appendChild(e);
  e.click();
  document.body.removeChild(e)
}

function launchMeeting() {
  let e = document.createElement('a');
  e.href = `http://localhost:8000/chat.html?username=${username}`;
  e.target = '_blank';
  document.body.appendChild(e);
  e.click();
  document.body.removeChild(e)
}

function logout() {
  localStorage.setItem('196532ac-ae33-4e85-952a-e3a969fa70bc-collablens', JSON.stringify({
    'currentAccount': ''
  }));
  window.location = 'http://localhost:8000'
}

if (JSON.parse(localStorage.getItem('196532ac-ae33-4e85-952a-e3a969fa70bc-collablens')).currentAccount != username) {
  window.location = 'http://localhost:8000';
}