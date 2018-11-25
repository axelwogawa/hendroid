# event_handler

from state_handler import State_handler

state_handler = State_handler()

def handle_event(event):
    key = event.replace("_event", "")
    print("event key \"" + key + "\" extracted")
    if(key in state_handler.get_states()):
        state_handler.change_state(key)
        
def register_observer(callback):
    state_handler.register_observer(callback)