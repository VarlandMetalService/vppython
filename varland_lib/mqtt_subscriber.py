import paho.mqtt.client as mqtt
from .functions import log_error
from varland_lib.recipe_manager import RecipeManager

class MQTTSubscriber:
    
    def __init__(self, cfg):
      self.cfg = cfg
      self.subscribe_to = cfg.get('mqtt_base_tag')
      self.broker_address = cfg.get('mqtt')['broker']
      self.port = cfg.get('mqtt')['port']
      self.client = mqtt.Client()
      self.client.on_connect = self.on_connect
      self.client.on_message = self.on_message
      self.connected = False
      self._connect_to_broker()

    def _connect_to_broker(self):
      try:
        self.client.connect(self.broker_address, self.port, 5)
        self.connected = True
      except Exception as e:
        log_error(e)

    def on_connect(self, client, userdata, flags, rc):
      print(f"Connected to MQTT broker at {self.broker_address}:{self.port}. Subscribing to {self.subscribe_to}.")
      self.client.subscribe(self.subscribe_to)

    def on_message(self, client, userdata, msg):
      variable_name = msg.topic.split('/')[-1]
      match variable_name:
        case 'i_Recipes_State':
          val = int(msg.payload.decode())
          if val == 2:
            pass
          elif val == 3:
            mgr = RecipeManager(self.cfg)
            mgr.save_to_files()

    def loop_forever(self):
      self.client.loop_forever()