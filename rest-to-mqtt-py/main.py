#!/usr/bin/python

import time
import sys
import json
import os
import subprocess
import select

from flask import Flask
from flask_restful import Api, Resource, reqparse

from cpEP import EdgeProtocolMQTT

MQTT_USER = os.getenv('MQTT_USER', None)
MQTT_PASS = os.getenv('MQTT_PASS', None)
project   = os.getenv('PROJECT_ID', None)
http_port = os.getenv('HTTP_PORT', 3000)

if project is None:
  print('You need to set the PROJECT_ID environmental variable')
  sys.exit(1)

if MQTT_USER is None or MQTT_PASS is None:
  print('You need to supply MQTT credentials to connect the Edge One MQTT Broker')
  sys.exit(1)

def jdebug(msg):
    try:
        json_str = json.dumps(msg, sort_keys=True, indent=4)
    except:
        json_str = "<JSON not returned>"
    print '%s' % (json_str)

def on_connect(mosq, obj, rc):
    if (rc == 0):
      print "Connected to Edge One MQTT Broker"

def on_message(mosq, obj, msg):
    print("Received on topic " + msg.topic + " (QoS: " + str(msg.qos) + "): " + str(msg.payload))
    jdebug(msg.payload)

app = Flask(__name__)
api = Api(app)

class Data(Resource):
  def post(self):
    parser = reqparse.RequestParser()
    parser.add_argument("name")
    args = parser.parse_args()

    data = { 'ts': int(time.time()), 'pid': project, 'g': 1, 'vals': [{ 'k': 'name', 'v': args['name'] }] }
    cpep.publish("data/"+project+"/1", json.dumps(data))

    return { 'success': True }

api.add_resource(Data, '/api/data')

def main():
    global cpep
    cpep = EdgeProtocolMQTT()

    # Assign event callbacks
    cpep.mqttc.on_message = on_message
    #cpep.mqttc.on_connect = on_connect
    #cpep.mqttc.on_subscribe = on_subscribe

    # Connect
    cpep.set_auth(MQTT_USER, MQTT_PASS)
    cpep.connect()
    cpep.mqttc.loop_start()

    app.run(port=http_port)

if __name__ == '__main__':
    main()
