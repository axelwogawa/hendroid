import websocket
import event_handler
from init import init

def on_message(ws, message):
    print("new message")
    data = message.split(":")
    event = data[1]+ "_event"
    if data[0] == "request":
        print("server requested state change event: " + event)
        event_handler.handle_event(event)

def on_state_change(new_state):
    print("state change triggered!")
    ws.send(new_state)

def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print("### opened ###")


# register hardware listeners
init();

event_handler.register_observer(on_state_change)

websocket.enableTrace(True)
ws = websocket.WebSocketApp(
    #"ws://hendroid.zosel.ch/",
    "ws://localhost:3030/",
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.on_open = on_open
ws.run_forever()