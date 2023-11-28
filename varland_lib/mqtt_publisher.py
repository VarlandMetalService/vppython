import paho.mqtt.client as mqtt
from .functions import log_error

class MQTTPublisher:
    
    def __init__(self, cfg):
      self.broker_address = cfg.get('mqtt')['broker']
      self.port = cfg.get('mqtt')['port']
      self.client = mqtt.Client()
      self.connected = False
      self._connect_to_broker()

    def _connect_to_broker(self):
      try:
        self.client.connect(self.broker_address, self.port, 5)
        self.connected = True
      except Exception as e:
        log_error(e)

    def publish(self, topic, value):
      try:
        if not self.connected:
          self._connect_to_broker()
          if not self.connected:
            raise Exception("Not connected to MQTT broker.")
        self.client.publish(topic, value, qos=1, retain=True)
      except Exception as e:
        log_error(e)

    def clear(self, topic):
      self.publish(topic, None)