# Load dependencies.
from varland_lib import global_config
from varland_lib.mqtt_subscriber import MQTTSubscriber

subscriber = MQTTSubscriber(global_config)
subscriber.loop_forever()