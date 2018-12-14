#import event_handler
import state_handler
from datetime import datetime, time

from socketIO_client_nexus import SocketIO, LoggingNamespace

def start(state_handler, timer_handler):
    #with SocketIO("hendroid.zosel.ch", 80, LoggingNamespace) as socketIO:
    with SocketIO("localhost", 3030, LoggingNamespace) as socketIO:
        
        def on_motion_request(request):
            print("client: new request: " + request)
            state_handler.handle_event(request + "_event")

        def on_state_change(new_state):
            print("client: state change observed at "
                  + datetime.now().isoformat(' ') + ": " + new_state)
            socketIO.emit('state changed', new_state)
        
        #careful, very much python in here!
        def auto_open(val):
            timer_handler.auto_open = val.lower() == "true"
        def auto_close(val):
            timer_handler.auto_close = val.lower() == "true"
        timer_actions = {"auto": {"open": auto_open
                                  ,"close": auto_close
                                  }
                         "time": {"open": time_open
                                  ,"close": time_close
                                  }
                         }
        def time_open(val):
            val_contents = val.split(":")
            timer_handler.open_time = time(hour=val_contents[0]
                                           ,minute=val_contents[1])
        def time_close(val):
            val_contents = val.split(":")
            timer_handler.close_time = time(hour=val_contents[0]
                                            ,minute=val_contents[1])
       
        def on_timer_request(request):
            print("client: new request: " + request)
            req_contents = request.split("-")
            timer_actions[req_contents[0]][req_contents[1]](req_contents[2])

        state_handler.register_observer(on_state_change)

        socketIO.on('motion request', on_motion_request)
        socketIO.on('set timer request', on_timer_request)
        socketIO.wait()
        print("client: socket stopped waiting forever o.O ("
              + datetime.now().isoformat(' ') + ")")
