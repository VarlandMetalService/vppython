# Load dependencies.
import time
from pycomm3 import LogixDriver
from .mqtt_publisher import MQTTPublisher
from .message_trigger import MessageTrigger
from .message_clearer import MessageClearer
from .functions import analyze_variable
import concurrent.futures

class Historizer:

  def __init__(self, cfg, mqtt=False, influx=False, messages=False):
    self.cfg = cfg
    self.publish_mqtt = mqtt
    self.publish_influx = influx
    self.publish_messages = messages
    self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    self.plc = LogixDriver(cfg.get('en_controller_ip'))
    self.plc.open()
    self._analyze_tags()
    self.mqtt_cache = {}
    self.groov_cache = {}
    self.groov_triggered = []

  def __del__(self):
    self.plc.close()
    self.executor.shutdown()

  def _analyze_tags(self):
    self.tags = []
    self.variables = {}
    tag_names = list(self.plc.tags.keys())
    for tag_name in tag_names:
      variable = analyze_variable(tag_name, tag_names)
      if (variable.publish_to_influxdb and self.publish_influx) or (variable.publish_to_mqtt and self.publish_mqtt) or ((variable.is_message_trigger or variable.is_message_clearer) and self.publish_messages):
        self.tags.append(tag_name)
        self.variables[tag_name] = variable

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
    timestamp = time.time_ns()
    tag_values = self.plc.read(*self.tags)
    if not isinstance(tag_values, list):
      tag_values = [tag_values]
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
      if variable.is_message_trigger and tag_val.value:
        if variable.tag not in self.groov_triggered:
          self.groov_triggered.append(variable.tag)
        trigger = MessageTrigger(self.cfg, self.plc, self.executor, variable.tag, variable.associated_variables, self.groov_cache)
      if variable.is_message_clearer and tag_val.value and variable.tag.replace('ClearWarning', 'TriggerWarning') in self.groov_triggered:
        self.groov_triggered.remove(variable.tag.replace('ClearWarning', 'TriggerWarning'))
        clearer = MessageClearer(self.cfg, self.plc, self.executor, variable.tag)
    if self.publish_influx:
      self.plc.write(('b_ResetHistorization', True))