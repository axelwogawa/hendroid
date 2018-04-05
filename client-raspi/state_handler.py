from threading import Timer
import outputs


class State_handler:
    
    def __init__(self):
        self.states = {'closed', 'closing', 'opened', 'opening'}
        self.state = 'closed'
        self.motion_interval = 12.0    #time interval after which motor motion will be stopped (in seconds)
        self.motion_timer = Timer(self.motion_interval, None)

    def set_state(self, string):
        if(string in self.states):
            self.state = string
        else:
            self.state = 'closed'
        return


    def change_state(self, new_state):
        success = False
        if(self.state != new_state):
            if(self.state == 'closed'):
                if(new_state == 'opening'):
                    success = True
            elif(self.state == 'opening'):
                if(new_state == 'opened' or new_state == 'closing'):
                    success = True
            elif(self.state == 'opened'):
                if(new_state == 'closing'):
                    success = True
            elif(self.state == 'closing'):
                if(new_state == 'opening' or new_state == 'closed'):
                    success = True
            
        if success:
            self.set_state(new_state)
            if (self.state == "opening" or self.state == "closing"):
                if(self.state == "opening"):
                    callback = outputs.open()
                else:
                    callback = outputs.close()
                self.motion_timer.cancel()
                self.motion_timer = Timer(self.motion_interval, callback)
            elif(self.state == "opened"):
                outputs.light_opened()
            elif(self.state == "closed"):
                outputs.light_closed()
            
        return success
