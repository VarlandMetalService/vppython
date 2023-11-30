# Load dependencies.
from .message_handler import MessageHandler

class MessageClearer(MessageHandler):

  def __init__(self, cfg, plc, executor, tag):
    super().__init__(cfg, plc, executor, tag)
    self._finish()