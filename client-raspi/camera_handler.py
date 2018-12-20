# Camera handling

from picamera import PiCamera
from datetime import datetime

camera = PiCamera()

def take_single_snapshot(path):
  filename = (path + datetime.strftime(datetime.now(), "%Y_%m_%d-%H:%M:%S") 
              + ".png")
  camera.capture(filename)
  return filename
