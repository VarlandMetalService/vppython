# Load dependencies.
import os
import sys
import re
import datetime
from collections import namedtuple
from . import global_config

# Create global function for logging errors.
def log_error(error):
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  msg = f"{timestamp}: {error}"
  try:
    print(f"{msg}", file=sys.stderr)
    with open(f"{os.getenv('LOCAL_PROJECT_PATH')}{global_config.get('error_log')}", 'a') as f:
      f.write(f"{msg}\n")
  except:
    pass

# Create global function for extracting variable details from tag names.
def analyze_variable(tag, tag_names):
  Variable = namedtuple('Variable',
                        ['tag',
                         'program',
                         'name',
                         'prefix',
                         'publish_to_influxdb',
                         'publish_to_mqtt',
                         'is_recipe_variable',
                         'is_message_trigger',
                         'is_message_clearer',
                         'associated_variables'])
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
  is_message_trigger = re.match(r"^b_\w+_TriggerWarning$", name) is not None
  is_message_clearer = re.match(r"^b_\w+_ClearWarning$", name) is not None
  associated_variables = []
  if prefix in ["ao", "ai", "do", "di"] or "h" in prefix:
    publish_to_influxdb = True
  if "m" in prefix:
    publish_to_mqtt = True
  if prefix in ["ri", "rf", "rb"]:
    is_recipe_variable = True
  if is_message_trigger:
    msg_id = re.match(r"^b_(\w+)_TriggerWarning$", name).group(1)
    associate_pattern = "" if program is None else f"^{program}\."
    associate_pattern += f"[a-z]+_{msg_id}_(?!TriggerWarning|ClearWarning)([\w]+)$"
    associate_regex = re.compile(associate_pattern)
    associated_variables = [var for var in tag_names if associate_regex.match(var) is not None]
  return Variable(tag,
                  program,
                  name,
                  prefix,
                  publish_to_influxdb,
                  publish_to_mqtt,
                  is_recipe_variable,
                  is_message_trigger,
                  is_message_clearer,
                  associated_variables)