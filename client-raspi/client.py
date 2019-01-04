#import event_handler
#import state_handler
import camera_handler as cam
from datetime import datetime, time
import time as pytime
from threading import Thread
from requests.exceptions import ConnectionError
from socketIO_client_nexus import SocketIO, LoggingNamespace


hosts = { "localhost":        { "port":     3030,
                                "socket":   None,
                                "interval": 0
                               }, 
          "hendroid.zosel.ch":{ "port":     80,
                                "socket":   None,
                                "interval": 6*60*60
                               }
         }

def start(state_handler, timer_handler, logger):
    ############################### general stuff ##############################
    def create_new_socket(host):
        #hack to create new socket to force new connection:
        global hosts
        logger.info("client: creating new socket to " + host)
        socket = hosts[host]["socket"]
        if(socket != None):
            hosts[host]["socket"] = None
            del socket
        connect(host)

    def on_full_request():
        state_handler.update_all_observers()
        timer_handler.update_all_observers()

    def on_disconnect():
        logger.warning("client: disconnected")
        global hosts
        for host in hosts:
            socket = hosts[host]["socket"]
            logger.info("client: connected to " + host + ": " 
                          + str(socket.connected))
            if(socket.connected == False):
                socket.connect()
                socket.emit("i am a raspi")
                pytime.sleep(2)
                logger.info("client: reconnected to " + host + ": " + 
                              str(socket.connected))
                if(socket.connected == False):
                    create_new_socket(host)
        #    else:
        #        #hack to force disconnection and proper reconnection
        #        # (reason: sometimes on_disconnect() is called, communication
        #        # stops, but all sockets pretend to be still connected)
        #        sockets[host].disconnect() 
        #        logger.warning("client: forced disconnect from " + host)


    ################################ motion stuff ##############################
    def on_motion_request(request):
        logger.info("client: new request: " + request)
        state_handler.handle_event(request + "_event")


    ################################ timer stuff ###############################
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
        logger.info("client: new timer request: " + request)
        req_contents = request.split("-")
        timer_actions[req_contents[0]][req_contents[1]](req_contents[2])
        
    
    ############################### image stuff ################################
    def on_image_request(request):
        logger.info("client: new image request: " + request)
        images = []
        if request == "single":
          images = [cam.take_single_snapshot(path)]
        #elif request == "sequence":


    ####################### single server connect routine ######################
    def connect(host):
        global hosts 
        with SocketIO(host, hosts[host]["port"], LoggingNamespace) as socketIO:
            hosts[host]["socket"] = socketIO
            logger.info("client: connected to " + host)
            socketIO.emit("i am a raspi")
            def on_state_change(new_state):
                logger.info("client: state change observed: " + new_state)
                socketIO.emit('state changed', new_state)
            
            def on_timer_change(update):
                logger.info("client: timer change observed: " + update)
                socketIO.emit('timer update', update)
            ############################ init routine ##########################
            try:
                state_handler.register_observer(on_state_change)
                timer_handler.register_observer(on_timer_change)

                socketIO.on('motion request', on_motion_request)
                socketIO.on('set timer request', on_timer_request)
                socketIO.on('full state request', on_full_request)
                socketIO.on('disconnect', on_disconnect)
                if(hosts[host]["interval"] <= 0):
                    socketIO.wait()
                else
                    socketIO.wait(hosts[host]["interval"]) #time in seconds
                logger.warning("client: " + host +
                                  " socket stopped waiting")
            except ConnectionError as e:
                logger.error('The server is down.', exc_info=True)
                raise
            except IndexError as e:
                logger.exception(str(e))
                create_new_socket(host)
            except Exception as e:
                logger.exception(str(e))
                raise

    ########################### connect to all servers #########################
    global hosts
    thread = Thread(target=connect, args=(host=hosts.keys()[0]))
    thread.start()
    
    while(True):
        create_new_socket(host=hosts.keys()[1])

    thread.join()
    logger.warning("Localhost websocket thread finished")
