#!/usr/bin/python

import time
import sys
import json
import os
import subprocess
import select

from cpEP import EdgeProtocolMQTT

MQTT_USER = os.getenv('MQTT_USER', None)
MQTT_PASS = os.getenv('MQTT_PASS', None)
file = os.getenv('FILE', None)
project = os.getenv('PROJECT_ID', None)
interval = os.getenv('INTERVAL', 5)

if file is None:
  print('You need to set the FILE environmental variable')

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

    f = subprocess.Popen(['tail', '-F', file], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    # Continue the network loop, exit when an error occurs
    rc = 0
    while (rc == 0):
      if p.poll(1):
        # TODO: unpack readline in multiple variables
        data = { 'ts': int(time.time()), 'pid': project, 'g': 1, 'vals': [{ 'k': 'line', 'v': f.stdout.readline() }] }
        cpep.publish("data/"+project+"/1", json.dumps(data))

      rc = cpep.loop(interval * 1000)
      print("loop rc: " + str(rc))

if __name__ == '__main__':
    main()
