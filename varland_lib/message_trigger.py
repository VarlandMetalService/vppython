# Load dependencies.
from .message_handler import MessageHandler

class MessageTrigger(MessageHandler):

  def __init__(self, cfg, plc, executor, tag, associated_variables, cache):
    super().__init__(cfg, plc, executor, tag)
    self.cache = cache
    self.tag_values = self.plc.read(*associated_variables)
    if not isinstance(self.tag_values, list):
      self.tag_values = [self.tag_values]
    for tag_val in self.tag_values:
      self._send_value(tag_val)
    self._finish()

  def _send_value(self, tag_value):
    value = tag_value.value
    var_name = tag_value.tag.split('.')[-1]
    prefix = var_name.split('_')[0] 
    url = f"https://{self.cfg.get('groov_hostname')}/pac/device/strategy/vars/?/{var_name}"
    match prefix:
      case 'b':
        url = url.replace('?', 'int32s')
        value = 1 if value else 0
      case 'i':
        url = url.replace('?', 'int32s')
      case 'f':
        url = url.replace('?', 'floats')
      case 's':
        url = url.replace('?', 'strings')
      case _:
        url = None
    if var_name in self.cache and self.cache[var_name] == value:
      return
    self.cache[var_name] = value
    if url is not None:
      self._send_to_groov(url, value)