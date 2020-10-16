import base64, random, string, math

''' Send images via MQTT

Taken from https://developer.ibm.com/recipes/tutorials/sending-and-receiving-pictures-from-a-raspberry-pi-via-mqtt/

Args:
    client (paho.mqtt.client.Client): MQTT client instance
    topic (str): MQTT topic to publish image data to
    image_path (str): path where png image is stored
    logger (logging.Logger): logger instance
'''

def send(client, topic, image_path, logger):
  # size of packet in bytes into which the image is going to be split
  packet_size=3000

  with open(image_path, "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read())
    end = packet_size
    start = 0
    length = len(encoded_image)
    picId = ''.join(random.choice(string.ascii_lowercase) for i in range(8))
    pos = 0
    no_of_packets = math.ceil(length/packet_size)
    while start <= len(encoded_image):
      data = {"data": encoded_image[start:end], "pic_id":picId, "pos": pos, "size": no_of_packets}
      client.publish(topic, json.JSONEncoder().encode(data))
      end += packet_size
      start += packet_size
      pos = pos +1
