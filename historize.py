# Load dependencies.
import time
from varland_lib import global_config
from varland_lib.historizer import Historizer

historizer = Historizer(global_config, mqtt=True, influx=True)
while True:
  historizer.historize()
  time.sleep(global_config.get('influx_metric_delay'))