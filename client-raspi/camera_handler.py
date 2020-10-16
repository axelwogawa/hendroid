# Camera handling

from picamera import PiCamera
from datetime import datetime
from time import sleep

camera = PiCamera()

''' Capture image via Raspi's camera module and store it on disk

Taken from https://developer.ibm.com/recipes/tutorials/sending-and-receiving-pictures-from-a-raspberry-pi-via-mqtt/

Args:
    path (str): path to directory where to store the image
    logger (logging.Logger): logger instance

Returns:
    filename (str): filename of image taken (incl. path prefix), if taking the
      image succeeded; None otherwise
'''

def take_single_snapshot(path, logger):
  filename = (path + datetime.strftime(datetime.now(), "%Y_%m_%d-%H:%M:%S")
              + ".png")
  try:
    logger.info("Capturing new image: " + filename)
    camera.start_preview()
    sleep(1)
    camera.capture(filename)
    camera.stop_preview()
  except Exception as e:
    logger.exception("Failed to capture image")
    logger.exception(str(e))
    filename = None
  finally:
    camera.close()
  return filename
