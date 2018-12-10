#Here the open and close timers are handled.

from apscheduler.schedulers.background import BackgroundScheduler
#from apschedulers.triggers import cron
from datetime import datetime, time
#import time
import pickle
import os

class Timer_handler:
    ############################### constructor ###############################
    def __init__(self, state_handler):
        self.boInit = True
        self._open_time = None
        self._close_time = None
        self._auto_open = None
        self._auto_close = None
        
        self.state_handler = state_handler
        self.scheduler = BackgroundScheduler()
        #read most recent settings saved to file, if available
        try:
            with open(os.environ['HOME'] + "/hendroid/client-raspi/timer_data.pkl", "rb") as input:
                self.open_time = pickle.load(input)
                print("internal: read <open_time> from file: "
                      + str(self.open_time))
                self.close_time = pickle.load(input)
                print("internal: read <close_time> from file: "
                      + str(self.close_time))
                self.auto_open = pickle.load(input)
                print("internal: read <auto_open> from file: "
                      + str(self.auto_open))
                self.auto_close = pickle.load(input)
                print("internal: read <auto_close> from file: "
                      + str(self.auto_close))
                self.boInit = False
        except Exception as e:
            print("internal error: timer state read from file: " + str(e))
            self.open_time = time(hour = 7, minute = 0)
            #time.strptime("7:00","%H:%M") #7:00am
            self.close_time = time(hour = 18, minute = 30)
            #time.strptime("18:30","%H:%M") #6:30pm
            self.auto_open = False
            self.boInit = False
            self.auto_close = False
            print("internal: set timer to default settings")
        #self.open_trigger = cron(hour = self.open_time.hour, minute = 0, second = 0)
        #self.close_trigger = cron(hour = 18, minute = 30, second = 0)
        self.scheduler.start()
    
    
    ########################### property definition ###########################
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
    
    
    ######################### property getters and setters ####################
    @auto_open.setter
    def auto_open(self, value):
        if self.auto_open == None or value != self.auto_open:
            self._auto_open = value
            if(self.scheduler.running):
                self.scheduler.pause()
            if(self.auto_open):
                self.scheduler.resume_job(job_id=self.open_job.id)
            else:
                self.scheduler.pause_job(job_id=self.open_job.id)
            print("internal: set <auto_open> to " + str(self.auto_open))
            if(self.scheduler.running):
                self.scheduler.resume()
            self.save_state()
    
    @auto_close.setter
    def auto_close(self, value):
        if self.auto_close == None or value != self.auto_close:
            self._auto_close = value
            if(self.scheduler.running):
                self.scheduler.pause()
            if(self.auto_close):
                self.scheduler.resume_job(job_id=self.close_job.id)
            else:
                self.scheduler.pause_job(job_id=self.close_job.id)
            print("internal: set <auto_close> to " + str(self.auto_close))
            if(self.scheduler.running):
                self.scheduler.resume()
            self.save_state()
    
    @open_time.setter
    def open_time(self, value):
        if self.open_time == None or value != self.open_time:
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
            if(self.scheduler.running):
                self.scheduler.resume()
            self.save_state()
            
    @close_time.setter
    def close_time(self, value):
        if self.close_time == None or value != self.close_time:
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
            if(self.scheduler.running):
                self.scheduler.resume()
            self.save_state()
    
    
    ############################## other methods ##############################
    def exec_motion(self, arg):
        print("internal: timing event - " + arg)
        self.state_handler.handle_event(arg + "_event")
    
    def save_state(self):
        if(self.boInit == False):
            try:
                with open(os.environ['HOME'] + "/hendroid/client-raspi/timer_data.pkl", "wb") as output:
                    pickle.dump(self.open_time, output)
                    pickle.dump(self.close_time, output)
                    pickle.dump(self.auto_open, output)
                    pickle.dump(self.auto_close, output)
                    print("internal: successfully saved timer settings to file")
            except Exception as e:
                print("internal error: timer setiings write to file: " + str(e))
    
    #TODO:
    #scheduler.shutdown()
    #connect timer_handler to event_handler
    #connect timing events to client