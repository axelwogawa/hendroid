#In this file, output handling is done. The classes Flasher and
# Flasher_handler are for making LEDs flash (as complicated as this because
# threading is neccessary to not block all other operations while endless-
# looping through on-off-procedure). The public methods further down actually
# switch hardware outputs on or off.

import pifacedigitalio as pfdio
import time
from threading import Thread


class Flasher(Thread):
    flashing = False
    interval = 0.5 #seconds
    lgts = None
    
    def __init__(self, lgts):
        self.lgts = lgts
        Thread.__init__(self)
        self.daemon = True
        self.start()
    
    def run(self):
        self.flashing = True
        while self.flashing:
            if not(self.lgts is None):
                for lgt in self.lgts:
                    lgt.toggle()
            time.sleep(self.interval)
        return
    
    def stop(self):
        self.flashing = False
        return


class Flasher_handler:
    flasher = None
    
    def flash(self, lgts):
        if not(self.flasher is None):
           self.flasher.stop()
        self.flasher = Flasher(lgts)
        return
    
    def stop(self):
        if not(self.flasher is None):
           self.flasher.stop()
        return


pfd = pfdio.PiFaceDigital()
flasher_handler = Flasher_handler()
flasher_handler.flash(None)

#outputs
rel_op = pfd.output_pins[0]  #the open motor relay
rel_cl = pfd.output_pins[1]  #the close motor relay
rel_ro = pfd.output_pins[2]  #the room light relay
lgt_op = pfd.output_pins[3]  #the led of the open button
lgt_cl = pfd.output_pins[4]  #the led of the close button


def open():
    rel_cl.turn_off()
    rel_op.turn_on()
    return

def close():
    rel_op.turn_off()
    rel_cl.turn_on()
    return

def stop():
    rel_op.turn_off()
    rel_cl.turn_off()
    return

def light_opened():
    flasher_handler.stop()
    lgt_cl.turn_off()
    lgt_op.turn_on()
    return

def light_closed():
    flasher_handler.stop()
    lgt_op.turn_off()
    lgt_cl.turn_on()
    return

def light_opening():
    flasher_handler.stop()
    lgt_op.turn_off()
    lgt_cl.turn_off()
    flasher_handler.flash([lgt_op])
    return

def light_closing():
    flasher_handler.stop()
    lgt_op.turn_off()
    lgt_cl.turn_off()
    flasher_handler.flash([lgt_cl])
    return

def light_intermediate():
    flasher_handler.stop()
    lgt_op.turn_off()
    lgt_cl.turn_off()
    flasher_handler.flash([lgt_op, lgt_cl])
    return

def light_off():
    flasher_handler.stop()
    lgt_op.turn_off()
    lgt_cl.turn_off()
    return