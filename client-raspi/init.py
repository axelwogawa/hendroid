#From here, input event listeners (i.e. listeners for button pushes or position
# switch signals) are registered and activated. An event triggers a state
# change. For states: see state_handler.py

import pifacedigitalio as pfdio
#from event_handler import Event_handler
from state_handler import State_handler
from client import start
from timer_handler import Timer_handler
from threading import Timer
import logging


############################### constants ###################################
#pin numbers of the inputs
pnum_btn_op = 0  #the open button
pnum_btn_cl = 3  #the close button
pnum_sns_op = 5  #the opened position sensor
pnum_sns_cl = 4  #the closed position sensor

#available states; need to be named consistantly to state_handler states (see
# state_handler.py)
states =    {pnum_btn_op: "opening"
            ,pnum_btn_cl: "closing"
            ,pnum_sns_op: "opened"
            ,pnum_sns_cl: "closed"
            ,404: "intermediate"
            }


################################## logging #####################################
logger = logging.getLogger("hendroid")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)
file_handler = loging.FileHandler(filename="hendroid.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG))


################################# HW handler ###################################
pfd = pfdio.PiFaceDigital()


############################ callback functions ##############################
#pass event string over to event handler
def handle_input_event(event):
    print("hardware: event detected at pin number " + str(event.pin_num))
    logger.info("hardware: event detected at pin number " + str(event.pin_num))
    print(event)
    #wait if input state persists for at least 500ms, otherwise dismiss event
    unbounce_timer = Timer( interval=0.5,  #time in seconds
                            function=state_handler.handle_event, 
                            args=[states[event.pin_num] + "_event"])
    unbounce_timer.start()
    while True:
      if (pfd.input_pins[event.pin_num] != event.direction or 
          unbounce_timer.isAlive() == False):
        print("hardware: event dismissed")
        logger.info("hardware: event dismissed")
        unbounce_timer.cancel()
        break


############################### init procedure ##############################
listener = pfdio.InputEventListener(chip=pfd)

#register input listeners
listener.register(pnum_btn_op, pfdio.IODIR_RISING_EDGE, handle_input_event)
listener.register(pnum_btn_cl, pfdio.IODIR_RISING_EDGE, handle_input_event)
listener.register(pnum_sns_op, pfdio.IODIR_FALLING_EDGE, handle_input_event)
listener.register(pnum_sns_cl, pfdio.IODIR_FALLING_EDGE, handle_input_event)
#listener.register(pnum_sns_op, pfdio.IODIR_RISING_EDGE, handle_input_event)
l#istener.register(pnum_sns_cl, pfdio.IODIR_RISING_EDGE, handle_input_event)
listener.activate()

print("internal: hardware listeners registered")
logger.info("internal: hardware listeners registered")

#initialise internal state
if(pfd.input_pins[pnum_sns_op].value):
    state_handler = State_handler(states[pnum_sns_op], logger)
elif(pfd.input_pins[pnum_sns_cl].value):
    state_handler = State_handler(states[pnum_sns_cl], logger)
else:
    state_handler = State_handler(states[404], logger)

timer_handler = Timer_handler(state_handler, logger)

#start nodejs socket
start(state_handler, timer_handler, logger)
