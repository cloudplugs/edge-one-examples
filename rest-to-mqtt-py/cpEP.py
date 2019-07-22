import paho.mqtt.client as mqtt

version = "1.0"

class EdgeProtocolMQTT(object):
    CP_KA   = 60*4.8
    CP_HOST = "172.42.0.1"
    CP_PORT = 1883
    CP_SSL  = False

    CP_OK = 0
    CP_FAIL = 1

    ##  Constructor
    #   @param self The object pointer
    def __init__(self):
        self.mqttc = mqtt.Client()

        # Assign event callbacks
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe

    def on_connect(self, userdata, mosq, obj, rc):
        if (rc == 0):
          print "Connected to MQTT Broker at %s:%s (%s)" % (self.CP_HOST, self.CP_PORT, "secure" if self.CP_SSL else "insecure")
        else:
          print "RC %d" % rc

    def on_message(self, mosq, obj, msg):
        print("Received on topic " + msg.topic + " (QoS: " + str(msg.qos) + "): " + str(msg.payload))
        jdebug(msg.payload)

    def on_publish(self, mosq, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mosq, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def set_auth(self, user, password):
        rc = self.mqttc.username_pw_set(username=user, password=password)
        return rc

    def connect(self):
        # Connect
        rc = self.mqttc.connect(self.CP_HOST, self.CP_PORT, self.CP_KA)
        return rc

    def subscribe(self, topic, qos):
        rc = self.mqttc.subscribe(topic, qos)
        return rc

    def publish(self, topic, msg):
        rc = self.mqttc.publish(topic, msg)
        return rc

    def loop(self, s):
        rc = self.mqttc.loop(s)
        return rc

