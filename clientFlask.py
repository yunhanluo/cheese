import flask, json

app = flask.Flask(__name__)

@app.route('/', methods = ['GET'])
def mainpage():
  with open('data\\data.json', 'r') as file:
    return json.loads(file.read())['chatHistory']

@app.route('/inputs', methods = ['POST'])
def inputPage():
  data = flask.request.json
  if data == None:
    return '0'
  val = data.get('value')
  return '1'

app.run('0.0.0.0', 2)