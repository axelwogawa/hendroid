#In here, the State_handler class is defined.
# It handles hendroid's current state (i.e. if hendroid is just opening,
# closed etc.) and state transitions. A state transition triggers the 
# according outputs to be switched on or off (i.e. motor relays, switch LEDs).
# A state transition will only happen, if it makes sense (i.e. opening ->
# closed is nonsense transition).
#For outputs handling: see outputs.py

from threading import Timer
import outputs

class State_handler:
    observers = []
    
    def register_observer(self, callback):
        print("registering observer")
        self.observers.append(callback)
        
    def __init__(self):
        self.states = {'closed', 'closing', 'opened', 'opening', 'intermediate'}
        self.state = 'intermediate'
        self.motion_interval = 12.0     #time interval after which motor motion
                                        # will be stopped (in seconds)
        self.motion_timer = Timer(self.motion_interval, None)

    def set_state(self, string):
        if(string in self.states):
            self.state = string
        else:
            self.state = 'intermediate'
        return
    
    def get_state(self):
        return self.state
    
    def get_states(self):
        return self.states


    def change_state(self, new_state):
        success = False
        
        #check state transition plausibility
        if(self.state == 'closed'):
            if(new_state == 'opening'):
                success = True
                
        elif(self.state == 'opening'):
            if(new_state == 'opened'\
               or new_state == 'intermediate'):
                success = True
            elif(new_state == 'closing'\
                 or new_state == 'opening'):
                success = True
                new_state = 'intermediate'
                
        elif(self.state == 'opened'):
            if(new_state == 'closing'):
                success = True
                
        elif(self.state == 'closing'):
            if(new_state == 'closed'\
               or new_state == 'intermediate'):
                success = True
            elif(new_state == 'opening' \
                 or new_state == 'closing'):
                success = True
                new_state = 'intermediate'
                
        elif(self.state == 'intermediate'):
            if(new_state == 'opening' \
               or new_state == 'closing'):
                success = True
            
        #in case of plausible state change: perform state change
        if success:
            self.set_state(new_state)
            self.motion_timer.cancel()
            if(self.state == "opening"):
                outputs.open()
                outputs.light_opening()
                #stop motor if it takes to long to open/close
                self.motion_timer = Timer(self.motion_interval, \
                                          self.motion_abort)
                self.motion_timer.start()
            elif(self.state == "closing"):
                outputs.close()
                outputs.light_closing()
                #stop motor if it takes to long to open/close
                self.motion_timer = Timer(self.motion_interval, \
                                          self.motion_abort)
                self.motion_timer.start()
            elif(self.state == "opened"):
                outputs.stop();
                outputs.light_opened()
            elif(self.state == "closed"):
                outputs.stop()
                outputs.light_closed()
            elif(self.state == "intermediate"):
                outputs.stop()
                outputs.light_off()
                
            print("New state: " + self.state)
            print("Calling " + str(len(self.observers)))
            [ callback(self.state) for callback in self.observers ]
            
        else:
            print("No state change")
            
        return success
    
    def motion_abort(self):
        self.change_state('intermediate')
        return