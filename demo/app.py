from flask import Flask, request
import requests
import threading

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, i\'m a flask server!'

@app.route("/motionRequest", methods=['POST'])
def on_motion_request():
    state = request.form.get('state')
    print("received motionRequest: {}".format(state))
    try:
        do_stuff(state)
        return 'Ok'
    except Exception as e:
        return str(e), 400

def do_stuff(state):
    if state in ['opening', 'closng']:
        threading.Timer(1, done).start()
        return True
    raise Exception('invalid state request: ' + state)

def done():
    r = requests.post("http://localhost:3031/stateChange", data={
        "new_state": "opening"
    })
    print(r.text)
