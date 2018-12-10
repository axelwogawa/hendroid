#import event_handler
import state_handler
from datetime import datetime

from socketIO_client_nexus import SocketIO, LoggingNamespace

def start(state_handler, timer_handler):
    with SocketIO("hendroid.zosel.ch", 80, LoggingNamespace) as socketIO:
    # with SocketIO("localhost", 3030, LoggingNamespace) as socketIO:
        
        def on_request(request):
            print("client: new request: " + request)
            state_handler.handle_event(request + "_event")

        def on_state_change(new_state):
            print("client: state change observed at " + datetime.now().isoformat(' ') + ": " + new_state)
            socketIO.emit('state changed', new_state)

        state_handler.register_observer(on_state_change)

        socketIO.on('request', on_request)
        socketIO.wait()