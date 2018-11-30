#Here the open and close timers are handled.

from apscheduler.schedulers.background import BackgroundScheduler

class Timer_handler:
    open_time = property(get_open_time, set_open_time)
    close_time = property(get_close_time, set_close_time)
    auto_open = property(get_auto_open, set_auto_open)
    auto_close = property(get_auto_close, set_auto_close)
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.open_time = "something"
        self.close_time = "something else"
        self.auto_open = False
        self.auto_close = False
    
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