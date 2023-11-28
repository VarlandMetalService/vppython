# Load dependencies.
import time
from datetime import datetime, timedelta
from pycomm3 import LogixDriver
from .mqtt_publisher import MQTTPublisher
from .functions import analyze_variable

class Historizer:

  def __init__(self, cfg):        
    self.cfg = cfg
    self.plc = LogixDriver(cfg.get('en_controller_ip'))
    self.plc.open()
    self._analyze_tags()
    self.mqtt_cache = {}

  def __del__(self):
    self.plc.close()

  def _analyze_tags(self):
    self.tags = []
    self.variables = {}
    tag_names = list(self.plc.tags.keys())
    for tag_name in tag_names:
      variable = analyze_variable(tag_name)
      if variable.publish_to_influxdb or variable.publish_to_mqtt:
        self.tags.append(tag_name)
        self.variables[tag_name] = variable
    self.last_retrieval = datetime.now()

  def _get_value(self, tag):
    match tag.type:
      case 'DINT' | 'BOOL' | 'INT':
        return int(tag.value)
      case 'TIMER':
        return float(tag.value['ACC']) / 1000.0
      case _:
        return float(tag.value)
  
  def historize(self):
    mqtt_pub = None
    if datetime.now() - self.last_retrieval > timedelta(seconds=600):
      self._analyze_tags()
    timestamp = time.time_ns()
    tag_values = self.plc.read(*self.tags)
    for tag_val in tag_values:
      variable = self.variables[tag_val.tag]
      if variable.publish_to_mqtt:
        topic = f"ab/{variable.name}" if variable.program is None else f"ab/{variable.program}/{variable.name}"
        val = self._get_value(tag_val)
        if topic not in self.mqtt_cache or self.mqtt_cache[topic] != val:
          if mqtt_pub is None:
            mqtt_pub = MQTTPublisher(self.cfg)
          self.mqtt_cache[topic] = val
          mqtt_pub.publish(topic, val)
      if variable.publish_to_influxdb:
        print(f"variables,name={variable.name},controller=aben.varland.com value={self._get_value(tag_val)} {timestamp}")
    self.plc.write(('b_ResetHistorization', True))