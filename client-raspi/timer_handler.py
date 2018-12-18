#In here, the Timer_handler class is defined.
# In it the open and close timers are handled by a cron job which again is
# handled by BackgroundScheduler module. For automatically opening and closing
# the door each at a given time, two BackgroundScheduler jobs are created. By
# setting Timer_handler's auto_-properties to True or False, automatic opening
# or closing, resp., can be switched on or off. By setting Timer_handler's
# _time-properties, the according times can be set. Changing one of these
# settings affects the according scheduler job to be changed accordingly. All
# settings are saved to a binary file by python's Pickle module. this is done
# at each value change. On Timer_handler class instanciation, these values are
# read back from the file into the object.

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time
import pickle
import os

class Timer_handler:
    settings_file = "/home/pi/hendroid/client-raspi/timer_data.pkl"
    ############################### constructor ###############################
    def __init__(self, state_handler, logger):
        self.boInit = True
        self._open_time = None
        self._close_time = None
        self._auto_open = None
        self._auto_close = None
        
        self.state_handler = state_handler
        self.scheduler = BackgroundScheduler()
        self.observers = []
        self.log = logger
        #read most recent settings saved to file, if available
        try:
            #with open(os.environ['HOME'] + 
            #"/hendroid/client-raspi/timer_data.pkl", "rb") as input:
            with open(self.settings_file, "rb") as input:
                self.open_time = pickle.load(input)
                print("internal: read <open_time> from file: "
                      + str(self.open_time))
                self.log.info("internal: read <open_time> from file: "
                      + str(self.open_time))
                self.close_time = pickle.load(input)
                print("internal: read <close_time> from file: "
                      + str(self.close_time))
                self.log.info("internal: read <close_time> from file: "
                      + str(self.close_time))
                self.auto_open = pickle.load(input)
                print("internal: read <auto_open> from file: "
                      + str(self.auto_open))
                self.log.info("internal: read <auto_open> from file: "
                      + str(self.auto_open))
                self.auto_close = pickle.load(input)
                print("internal: read <auto_close> from file: "
                      + str(self.auto_close))
                self.log.info("internal: read <auto_close> from file: "
                      + str(self.auto_close)
                self.boInit = False
        except Exception as e:
            print("internal error: timer state read from file: " + str(e))
            self.log.error("internal error: timer state read from file: ", 
                            exc_info=True)
            self.open_time = time(hour = 7, minute = 0)
            self.close_time = time(hour = 18, minute = 30)
            self.auto_open = False
            self.boInit = False
            self.auto_close = False
            print("internal: set timer to default settings")
            self.log.info("internal: set timer to default settings")
        self.scheduler.start()
    
    
    ########################### property definition ###########################
    #Attrinutes are defined as properties as changing them requires some effort
    # (i.e. changing the Scheduler settings accordingly) rather than changing
    # them directly.
    @property
    def open_time(self):
        return self._open_time
    
    @property
    def close_time(self):
        return self._close_time
    
    @property
    def auto_open(self):
        return self._auto_open
    
    @property
    def auto_close(self):
        return self._auto_close
    
    @auto_open.setter
    def auto_open(self, value):
        if (isinstance(value, bool) 
            and value != None
            and (self.auto_open == None or value != self.auto_open)):
            self._auto_open = value
            if(self.scheduler.running):
                self.scheduler.pause()
            if(self.auto_open):
                self.scheduler.resume_job(job_id=self.open_job.id)
            else:
                self.scheduler.pause_job(job_id=self.open_job.id)
            print("internal: set <auto_open> to " + str(self.auto_open))
            self.log.info("internal: set <auto_open> to " + str(self.auto_open))
            if(self.scheduler.running):
                self.scheduler.resume()
            self.save_state()
            self.notify_observers("auto-open")
    
    @auto_close.setter
    def auto_close(self, value):
        if (isinstance(value, bool) 
            and value != None
            and (self.auto_close == None or value != self.auto_close)):
            self._auto_close = value
            if(self.scheduler.running):
                self.scheduler.pause()
            if(self.auto_close):
                self.scheduler.resume_job(job_id=self.close_job.id)
            else:
                self.scheduler.pause_job(job_id=self.close_job.id)
            print("internal: set <auto_close> to " + str(self.auto_close))
            self.log.info("internal: set <auto_close> to " + 
                            str(self.auto_close))
            if(self.scheduler.running):
                self.scheduler.resume()
            self.save_state()
            self.notify_observers("auto-close")
            
    @open_time.setter
    def open_time(self, value):
        if (isinstance(value, time) 
            and value != None
            and (self.open_time == None or value != self.open_time)):
            self._open_time = value
            if(self.scheduler.running):
                self.scheduler.pause()
            self.open_job = self.scheduler.add_job(self.exec_motion
                                                  ,trigger="cron"
                                                  ,args=["opening"]
                                                  ,id="jopen"
                                                  ,name="open_job"
                                                  ,max_instances=1
                                                  ,replace_existing=True
                                                  ,hour = self.open_time.hour
                                                  ,minute = self.open_time.minute
                                                  )
            print("internal: set <open_time> to " + str(self.open_time))
            self.log.info("internal: set <open_time> to " + str(self.open_time))
            if(self.scheduler.running):
                self.scheduler.resume()
            self.save_state()
            self.notify_observers("time-open")
            
    @close_time.setter
    def close_time(self, value):
        if (isinstance(value, time) 
            and value != None
            and (self.close_time == None or value != self.close_time)):
            self._close_time = value
            if(self.scheduler.running):
                self.scheduler.pause()
            self.close_job = self.scheduler.add_job(self.exec_motion
                                                    ,trigger="cron"
                                                    ,args=["closing"]
                                                    ,id="jclose"
                                                    ,name="close_job"
                                                    ,max_instances=1
                                                    ,replace_existing=True
                                                    ,hour = self.close_time.hour
                                                    ,minute = self.close_time.minute
                                                    )
            print("internal: set <close_time> to " + str(self.close_time))
            self.log.info("internal: set <close_time> to " + 
                            str(self.close_time))
            if(self.scheduler.running):
                self.scheduler.resume()
            self.save_state()
            self.notify_observers("time-close")
    
    
    ############################## other methods ##############################
    def register_observer(self, callback):
        print("internal: registering timer observer")
        self.log.info("internal: registering timer observer")
        self.observers.append(callback)
        self.update_observer(callback)
        
    #Update all observers of the object, i.e. notify them about values
    # of all properties of the object.
    def update_all_observers(self):
        [ self.update_observer(callback) for callback in self.observers ]
        
    #Update observer defined by callback parameter, i.e. notify it about values
    # of all properties of the object.
    def update_observer(self, callback):       
        self.notify_observers("auto-open", [callback])
        self.notify_observers("auto-close", [callback])
        self.notify_observers("time-open", [callback])
        self.notify_observers("time-close", [callback])
        
    # notify given observers about changes encoded in update parameter
    # update parameter must have the form: "<cat>-<subcat>" with
    # cat in {"auto", "time"} and subcat in {"open", "close"}.
    # If observers parameter is omittet, then all registered observers of the
    # object are notified.
    def notify_observers(self, update, observers=None):
        if(self.boInit == False):
            update_vals = {"time-open":   [self.open_time.hour
                                          ,self.open_time.minute]
                           ,"time-close": [self.close_time.hour
                                          ,self.close_time.minute]
                           ,"auto-close": [self.auto_close]
                           ,"auto-open":  [self.auto_open]
                           }
            val_str = ""
            for val in update_vals[update]:
                val_str = val_str + ":" + str(val) 
            update = update + "-" + val_str[1:]
            if(observers == None):
                observers = self.observers
            print("internal: Calling " + str(len(observers)) + " timer observers")
            self.log.info("internal: Calling " + str(len(observers)) + 
                            " timer observers")
            [ callback(update) for callback in observers ]
        
    def exec_motion(self, arg):
        print("internal: scheduled event (" + datetime.now().isoformat(' ')
              + ") - " + arg)
        self.log("internal: scheduled event - " + arg)
        self.state_handler.handle_event(arg + "_event")
    
    def save_state(self):
        if(self.boInit == False):
            try:
                #with open(os.environ['HOME'] + "/hendroid/client-raspi/"
                 #         + "timer_data.pkl", "wb") as output:
                with open(self.settings_file, "wb") as output:
                    pickle.dump(self.open_time, output)
                    pickle.dump(self.close_time, output)
                    pickle.dump(self.auto_open, output)
                    pickle.dump(self.auto_close, output)
                    print("internal: successfully saved timer setting to file")
                    self.log.info("internal: successfully saved timer setting" +
                                    " to file")
            except Exception as e:
                print("internal error: write timer setting to file: " + str(e))
                self.log.error("internal error: write timer setting to file: ",
                                exec_info=True)
    
    def __del__(self):
        self.scheduler.shutdown()
