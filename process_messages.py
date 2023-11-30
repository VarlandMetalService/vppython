# Load dependencies.
import time
from varland_lib import global_config
from varland_lib.historizer import Historizer

historizer = Historizer(global_config, messages=True)
while True:
  historizer.historize()
  time.sleep(global_config.get('log_delay'))