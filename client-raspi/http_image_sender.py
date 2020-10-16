import requests

''' Send images via HTTP

Args:
    url (str): server address
    image_path (str): path where png image is stored
    logger (logging.Logger): logger instance
'''

def send(url, image_path, logger):
  with open(image_path, "rb") as image_file:
    logger.info("Sending image to " + url)
    x = requests.post(url, data = image_file)
    logger.info("Reply: " + x.text)
