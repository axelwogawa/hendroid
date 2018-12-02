#Here the open and close timers are handled.

from apscheduler.schedulers.background import BackgroundScheduler
from apschedulers.triggers import cron
from datetime import datetime, time
#import time

class Timer_handler:
    open_time = property(get_open_time, set_open_time)
    close_time = property(get_close_time, set_close_time)
    auto_open = property(get_auto_open, set_auto_open)
    auto_close = property(get_auto_close, set_auto_close)
    
    def __init__(self):
        self.open_time = time(hour = 7, minute = 0)#time.strptime("7:00","%H:%M") #7:00am
        self.close_time = time(hour = 18, minute = 30)#time.strptime("18:30","%H:%M") #6:30pm
        self.auto_open = False
        self.auto_close = False
        #self.open_trigger = cron(hour = self.open_time.hour, minute = 0, second = 0)
        #self.close_trigger = cron(hour = 18, minute = 30, second = 0)
        self.scheduler = BackgroundScheduler()
        self.open_job = scheduler.add_job(exec_motion
                                          ,trigger="cron"
                                          ,args=["opening"]
                                          ,id="jopen"
                                          ,name="open_job"
                                          ,max_instances=1
                                          ,replace_existing=True
                                          ,hour = self.open_time.hour
                                          ,minute = self.open_time.minute
                                          )
    
    def get_auto_open(self):
        return self.auto_open
    
    def set_auto_open(self, value):
        if value != self.auto_open:
            if value == True:
                %enable auto_opening
            else
                %disable auto_opening
            self.auto_open = value
    
    def get_auto_close(self):
        return self.auto_close
    
    def set_auto_close(self, value):
        if value != self.auto_close:
            if value == True:
                %enable auto_closing
            else
                %disable auto_closing
            self.auto_close = value
    
    def get_open_time(self):
        return self.open_time
    
    def set_open_time(self, value):
        if value != self.open_time:
            %reset schedule time
            self.open_time = value
    
    def get_close_time(self):
        return self.close_time
    
    def set_close_time(self, value):
        if value != self.close_time:
            %reset schedule time
            self.close_time = value
    
    %TODO:
    %set up times correctly
    %add job
    %start/pause job
    %scheduler.shutdown()
    %connect timer_handler to event_handler
    %connect timing events to client