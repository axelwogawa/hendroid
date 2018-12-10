# event_handler

from state_handler import State_handler
class Event_handler:
    def __init__(self, state):
        self.state_handler = State_handler(state)

    def handle_event(self, event):
        key = event.replace("_event", "")
        print("internal: event key \"" + key + "\" extracted")
        if(key in self.state_handler.get_states()):
            self.state_handler.change_state(key)
            
    def register_observer(self, callback):
        self.state_handler.register_observer(callback)
