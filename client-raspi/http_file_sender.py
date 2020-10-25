import requests

def send(url, path, logger):
  ''' Send file Base64 encoded via HTTP

  Args:
      url (str): server address
      path (str): path where file is stored
      logger (logging.Logger): logger instance
  '''
  with open(path, "rb") as file:
    logger.info("Sending file to " + url)
    resp = requests.post(url, files = {"file": file.read()})
    logger.info("Response: " + resp.text)
