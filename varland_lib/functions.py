# Load dependencies.
import sys
import datetime
from collections import namedtuple
from . import global_config

# Create global function for logging errors.
def log_error(error):
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  msg = f"{timestamp}: {error}"
  try:
    print(f"{msg}", file=sys.stderr)
    with open(global_config.get('error_log'), 'a') as f:
      f.write(f"{msg}\n")
  except:
    pass

# Create global function for extracting variable details from tag names.
def analyze_variable(tag):
  Variable = namedtuple('Variable', ['tag', 'program', 'name', 'prefix', 'publish_to_influxdb', 'publish_to_mqtt', 'is_recipe_variable'])
  parts = tag.split('.')
  if len(parts) == 1:
    program = None
    name = parts[0]
  else:
    program = parts[0]
    name = parts[1]
  prefix = name.split('_')[0]
  publish_to_influxdb = False
  publish_to_mqtt = (name == "i_Recipes_State")
  is_recipe_variable = False
  match prefix:
    case "ao" | "ai" | "do" | "di":
      publish_to_influxdb = True
    case _ if "h" in prefix:
      publish_to_influxdb = True
    case _ if "m" in prefix:
      publish_to_mqtt = True
    case "ri" | "rf" | "rb":
      is_recipe_variable = True
  return Variable(tag, program, name, prefix, publish_to_influxdb, publish_to_mqtt, is_recipe_variable)