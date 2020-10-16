'''
TODO: payload string encoding -> JSON structure
TODO: camera control
'''
import os, logging
from datetime import time #, datetime
# import time as pytime
# from threading import Thread
# from requests.exceptions import ConnectionError
# from flask import Flask, request
# import requests as http

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

import camera_handler, mqtt_image_sender

load_dotenv()

# path to store images at
image_dir = "."

logger = None
client = None
state_handler = None
timer_handler = None


############################### callbacks ################################
'''Callback to handle image request from server -> take image, send back'''
def on_image_request(request):
    logger.info("client: new image request: " + request)
    image_path = None
    if request == "single":
      image_path = camera_handler.take_single_snapshot(image_dir, logger)
    #elif request == "sequence":
    if image_path:
      mqtt_image_sender.send(client, "images", image_path, logger)

'''Callback to handle internal state change -> send new state to server'''
def on_state_change(new_state):
    logger.info("client: state change observed: " + new_state)
    client.publish("stateChange", new_state)

'''Callback to handle internal timer update -> send new timer parameters to server '''
def on_timer_update(update):
    logger.info("client: timer change observed: " + update)
    client.publish("timerUpdate", update)

'''Callback to handle full request from server -> send current state and timer parameters to server'''
def on_full_request(_):
    try:
        state_handler.update_all_observers()
        timer_handler.update_all_observers()
    except Exception as e:
        logger.exception(str(e))

'''Callback to handle motion request from server -> swtich motion state'''
def on_motion_request(state):
    logger.info("client: new request: {}".format(state))
    try:
        result = state_handler.handle_event(state)
        logger.info("motion request: " + result)
    except Exception as e:
        logger.exception(str(e))

#careful, very much python in here!
def auto_open(val):
    val = val.lower()
    if val == "true" or val == "false":
        timer_handler.auto_open = val == "true"
def auto_close(val):
    val = val.lower()
    if val == "true" or val == "false":
        timer_handler.auto_close = val == "true"
def time_open(val):
    vals = val.split(":")
    if len(vals) == 2:
        if vals[0] == "":
            vals[0] = '0'
        if vals[1] == "":
            vals[1] = '0'
        timer_handler.open_time = time(hour=int(vals[0])
                                       ,minute=int(vals[1]))
def time_close(val):
    vals = val.split(":")
    if len(vals) == 2:
        if vals[0] == "":
            vals[0] = '0'
        if vals[1] == "":
            vals[1] = '0'
        timer_handler.close_time = time(hour=int(vals[0]), minute=int(vals[1]))

timer_actions = {
    "auto": {
        "open": auto_open,
        "close": auto_close
    },
    "time": {
        "open": time_open,
        "close": time_close
    }
}

'''Callback to handle timer update request from server -> set new timer parameters'''
def on_timer_request(payload):
    logger.info("client: new timer request: " + payload)
    req_contents = payload.split("-")
    try:
        timer_actions[req_contents[0]][req_contents[1]](req_contents[2])
    except Exception as e:
        logger.exception(str(e))

# dictionary: mqtt topic -> callback
handlers = {
  "fullRequest": on_full_request,
  "motionRequest": on_motion_request,
  "timerRequest": on_timer_request,
  "imageRequest": on_image_request,
}

'''The callback for when the client receives a CONNACK response from the server.'''
def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code "+str(rc))

    client.publish("hello", "It's me")

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    for topic in handlers:
      logger.info("Subscribing to MQTT topic: " + topic)
      client.subscribe(topic)

'''The callback for when a PUBLISH message is received from the server.'''
def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    try:
        print("received message: " + msg.topic + ", payload: " + payload)
        handler = handlers.get(msg.topic)
        if not handler:
            print("Received unknown message with topic " + msg.topic)
        handler(payload)
    except Exception as e:
        logger.exception(str(e))


############################ init routine ##########################
def start(state_handler_, timer_handler_, logger_):
    global state_handler, timer_handler, logger, client
    state_handler = state_handler_
    timer_handler = timer_handler_
    logger = logger_
    client = mqtt.Client()
    try:
        state_handler.register_observer(on_state_change)
        timer_handler.register_observer(on_timer_update)

        client.on_connect = on_connect
        client.on_message = on_message

        client.username_pw_set(os.getenv("MQTT_USER"), os.getenv("MQTT_PASSWORD"))
        client.connect(os.getenv("MQTT_HOST"), 1883, 10)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()

    except Exception as e:
        logger.exception(str(e))
        raise

if __name__ == '__main__':
    logger = logging.getLogger("hendroid client stub")
    start(None, None, logger)
