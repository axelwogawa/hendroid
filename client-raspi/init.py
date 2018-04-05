import pifacedigitalio as pfdio
from state_handler import State_handler


pfd = pfdio.PiFaceDigital()
listener = pfdio.InputEventListener(chip=pfd)
state_handler = State_handler()


#pin numbers of the inputs
pnum_btn_op = 0  #the open button
pnum_btn_cl = 3  #the close button
pnum_sns_op = 5  #the open position sensor
pnum_sns_cl = 4  #the closed position sensor


states =    {pnum_btn_op: "opening"
            ,pnum_btn_cl: "closing"
            ,pnum_sns_op: "opened"
            ,pnum_sns_cl: "closed"
            }


def handle_input_event(event):
    str1 = "event detected at pin number " + str(event.pin_num)
    print(str1)
    if(state_handler.change_state(states[event.pin_num])):
        print("New state: " + states[event.pin_num])
    else:
        print("No state change")
    return


#register input listeners
listener.register(pnum_btn_op, pfdio.IODIR_RISING_EDGE, handle_input_event)
listener.register(pnum_btn_cl, pfdio.IODIR_RISING_EDGE, handle_input_event)
listener.register(pnum_sns_op, pfdio.IODIR_FALLING_EDGE, handle_input_event)
listener.register(pnum_sns_cl, pfdio.IODIR_FALLING_EDGE, handle_input_event)
listener.activate()

print("listeners registered")