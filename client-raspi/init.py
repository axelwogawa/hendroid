#From here, input event listeners (i.e. listeners for button pushes or position
# switch signals) are registered and activated. An event triggers a state
# change. For states: see state_handler.py

import pifacedigitalio as pfdio
import event_handler
from client import start


#pin numbers of the inputs
pnum_btn_op = 0  #the open button
pnum_btn_cl = 3  #the close button
pnum_sns_op = 5  #the opened position sensor
pnum_sns_cl = 4  #the closed position sensor

#available states; need to be named consistantly to state_handler states (see
# state_handler.py)
states =    {pnum_btn_op: "opening_event"
            ,pnum_btn_cl: "closing_event"
            ,pnum_sns_op: "opened_event"
            ,pnum_sns_cl: "closed_event"
            }

#pass event string over to event handler
def handle_input_event(event):
    str1 = "event detected at pin number " + str(event.pin_num)
    print(str1)
    event_handler.handle_event(states[event.pin_num])

pfd = pfdio.PiFaceDigital()
listener = pfdio.InputEventListener(chip=pfd)

#register input listeners
listener.register(pnum_btn_op, pfdio.IODIR_RISING_EDGE, handle_input_event)
listener.register(pnum_btn_cl, pfdio.IODIR_RISING_EDGE, handle_input_event)
listener.register(pnum_sns_op, pfdio.IODIR_FALLING_EDGE, handle_input_event)
listener.register(pnum_sns_cl, pfdio.IODIR_FALLING_EDGE, handle_input_event)
listener.activate()

#TODO: create output listeners to make state changes in case of trouble
# possible (e.g. state == opening and motor fails -> state will always remain
# opening. Must this be prevented?)
#TODO: create timing event to trigger opening or closing by time
#TODO: connect server input events
#TODO: notify server in case of state change

print("hardware listeners registered")

#start socket
start()