#import event_handler
import state_handler
from datetime import datetime, time

from socketIO_client_nexus import SocketIO, LoggingNamespace

def start(state_handler, timer_handler):
    #with SocketIO("hendroid.zosel.ch", 80, LoggingNamespace) as socketIO:
    with SocketIO("localhost", 3030, LoggingNamespace) as socketIO:
        
        ########################## motion state stuff #########################
        def on_motion_request(request):
            print("client: new request: " + request)
            state_handler.handle_event(request + "_event")

        def on_state_change(new_state):
            print("client: state change observed at "
                  + datetime.now().isoformat(' ') + ": " + new_state)
            socketIO.emit('state changed', new_state)
        
        ############################# timer stuff #############################
        #careful, very much python in here!
        def auto_open(val):
            val = val.lower()
            if val == "true" or val == "false":
                timer_handler.auto_open = val == "true"
        def auto_close(val):
            val = val.lower()
            if val == "true" or val == "false":
                timer_handler.auto_close = val == "true"
        def time_open(val):
            vals = val.split(":")
            if len(vals) == 2:
                if vals[0] == "":
                    vals[0] = '0'
                if vals[1] == "":
                    vals[1] = '0'
                timer_handler.open_time = time(hour=int(vals[0])
                                               ,minute=int(vals[1]))
        def time_close(val):
            vals = val.split(":")
            if len(vals) == 2:
                if vals[0] == "":
                    vals[0] = '0'
                if vals[1] == "":
                    vals[1] = '0'
                timer_handler.close_time = time(hour=int(vals[0])
                                            ,minute=int(vals[1]))
        timer_actions = {"auto": {"open": auto_open
                                  ,"close": auto_close
                                  }
                         ,"time": {"open": time_open
                                   ,"close": time_close
                                   }
                         }
       
        def on_timer_request(request):
            print("client: new request: " + request)
            req_contents = request.split("-")
            timer_actions[req_contents[0]][req_contents[1]](req_contents[2])
        
        def on_timer_change(update):
            print("client: timer change observed at "
                  + datetime.now().isoformat(' ') + ": " + update)
            socketIO.emit('timer update', update)
        
        def on_full_request():
            state_handler.update_all_observers()
            timer_handler.update_all_observers()

        ############################## init routine ###########################
        try:
            state_handler.register_observer(on_state_change)
            timer_handler.register_observer(on_timer_change)

            socketIO.on('motion request', on_motion_request)
            socketIO.on('set timer request', on_timer_request)
            socketIO.on('full state request', on_full_request)
            socketIO.wait()
            print("client: socket stopped waiting forever o.O ("
                  + datetime.now().isoformat(' ') + ")")
        except ConnectionError as e:
            print('The server is down. Try again later.')
            print(e)
