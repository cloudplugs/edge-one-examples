#!/usr/bin/python

import time
import sys
import json
import os

import Adafruit_DHT
#import ds18b20
from cpEP import EdgeProtocolMQTT

MQTT_USER = os.getenv('MQTT_USER', None)
MQTT_PASS = os.getenv('MQTT_PASS', None)
sensor = os.getenv('SENSOR', None)
pin = os.getenv('PIN', None)
project = os.getenv('PROJECT_ID', None)
interval = os.getenv('INTERVAL', 5)

sensor_args = { '11': Adafruit_DHT.DHT11,
                '22': Adafruit_DHT.DHT22,
                '2302': Adafruit_DHT.AM2302,
                'DS18B20': 99 }
if pin is not None and sensor in sensor_args:
  sensor = sensor_args[sensor]
else:
  print('You need to set SENSOR and PIN environmental variables')
  sys.exit(1)

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

def loop_ds18b20():
  temp_c, temp_f = ds18b20.read_temp()
  if temp_c is not None:
    print('Temp={0:0.1f}* C'.format(temp_c))

    # Publish the reading
    #data = {'data': '{0:0.1f}'.format(temp_c) }
    #cpep.publish("data/"+project+"/temp", json.dumps(data))

    data = { 'ts': int(time.time()), 'pid': project, 'g': 1, 'vals': [{ 'k': 'temp', 'v': float('{0:0.1f}'.format(temp_c)) }] }
    cpep.publish("data/"+project+"/1", json.dumps(data))
  else:
    print('Failed to get reading')

def loop_dht():
  humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

  if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}  Humidity={1:0.1f}%'.format(temperature, humidity))

    # Publish the reading
    #data = {'data': { 'temp': '{0:0.1f}'.format(temperature), 'hum': '{0:0.1f}'.format(humidity) }}
    #cpep.publish("data/"+project+"/dht", json.dumps(data))

    data = { 'ts': int(time.time()), 'pid': project, 'g': 1, 'vals': [{ 'temp': float('{0:0.1f}'.format(temperature)), 'hum': float('{0:0.1f}'.format(humidity)) }] }
    cpep.publish("data/"+project+"/1", json.dumps(data))
  else:
    print('Failed to get reading')

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

    # Continue the network loop, exit when an error occurs
    rc = 0
    while (rc == 0):
      if sensor == 99:
        loop_ds18b20()
      else:
        loop_dht()
      rc = cpep.loop(interval * 1000)
      print("loop rc: " + str(rc))

if __name__ == '__main__':
    main()
