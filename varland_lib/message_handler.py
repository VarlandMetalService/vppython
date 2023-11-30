# Load dependencies.
import os
import json
import requests

class MessageHandler:

  def __init__(self, cfg, plc, executor, tag):
    self.cfg = cfg
    self.tag = tag
    self.plc = plc
    self.executor = executor

  def _finish(self):
    self._send_to_groov(f"https://{self.cfg.get('groov_hostname')}/pac/device/strategy/vars/int32s/{self.tag.split('.')[-1]}", 1)
    self._reset_ab_flag()

  def _reset_ab_flag(self):
    self.plc.write((self.tag, False))

  def _send_to_groov(self, url, value):
    var = url.split('/')[-1]
    match var:
      case _ if var.endswith('TriggerWarning'):
        emoji = '🔔'
      case _ if var.endswith('ClearWarning'):
        emoji = '🔕'
      case _:
        emoji = '🔹'
    print(f"{emoji} {var}: {value}")
    self._post_to_groov(url, value, f"{os.getenv('LOCAL_PROJECT_PATH')}config/epicen.pem")

  def _post_to_groov(self, url, value, cert):
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'apiKey': self.cfg.get('groov_api_key')
    }
    data = { 'value': value }
    self.executor.submit(requests.post, url, headers=headers, data=json.dumps(data), verify=cert)