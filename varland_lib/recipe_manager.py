# Load dependencies.
from pycomm3 import LogixDriver
from .functions import analyze_variable
import os
import json
import paramiko
from scp import SCPClient

class RecipeManager:

  def __init__(self, cfg):
    self.local_dir = cfg.get('local_recipe_dir')
    self.ssh = paramiko.SSHClient()
    self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self.ssh.connect(cfg.get('scp')['server'], username=cfg.get('scp')['username'], password=cfg.get('scp')['password'])
    self.scp = SCPClient(self.ssh.get_transport())
    self.remote_dir = cfg.get('scp')['recipe_dir']
    self.plc = LogixDriver(cfg.get('en_controller_ip'))
    self.plc.open()
    self._analyze_tags()

  def __del__(self):
    self.plc.close()
    self.scp.close()
    self.ssh.close()

  def _analyze_tags(self):
    self.tags = []
    self.variables = {}
    tag_names = list(self.plc.tags.keys())
    for tag_name in tag_names:
      variable = analyze_variable(tag_name)
      if variable.is_recipe_variable:
        self.tags.append(tag_name)
        self.variables[tag_name] = variable

  def _empty_local_dir(self):
    file_list = os.listdir(self.local_dir)
    for file_name in file_list:
      file_path = os.path.join(self.local_dir, file_name)
      if os.path.isfile(file_path):
        os.remove(file_path)

  def save_to_files(self):
    self._empty_local_dir()
    tag_values = self.plc.read(*self.tags)
    if not isinstance(tag_values, list):
      tag_values = [tag_values]
    for tag_val in tag_values:
      variable = self.variables[tag_val.tag]
      json_obj = {
        "tag": variable.tag,
        "value": tag_val.value,
      }
      file_name = f"{variable.tag.replace('Program:', '')}.json"
      file_path = os.path.join(self.local_dir, file_name)
      with open(file_path, 'w') as f:
        f.write(json.dumps(json_obj, indent=2))
    self._transfer_files_to_server()
    self._empty_local_dir()
    self.reset_recipe_state()

  def restore_from_files(self):
    self._empty_local_dir()
    self._transfer_files_from_server()
    file_list = os.listdir(self.local_dir)
    for file_name in file_list:
      file_path = os.path.join(self.local_dir, file_name)
      with open(file_path, 'r') as f:
        json_obj = json.loads(f.read())
      tag = json_obj['tag']
      value = json_obj['value']
      self.plc.write((tag, value))
    self._empty_local_dir()
    self.reset_recipe_state()

  def _transfer_files_to_server(self):
    self.ssh.exec_command(f'rm {self.remote_dir}/*')
    files = os.listdir(self.local_dir)
    for file_name in files:
      file_path = os.path.join(self.local_dir, file_name)
      remote_path = os.path.join(self.remote_dir, file_name)
      self.scp.put(file_path, remote_path)

  def _transfer_files_from_server(self):
    stdin, stdout, stderr = self.ssh.exec_command(f'ls {self.remote_dir}')
    files = stdout.read().splitlines()
    for file_name in files:
      remote_path = os.path.join(self.remote_dir, file_name.decode())
      local_path = os.path.join(self.local_dir, file_name.decode())
      self.scp.get(remote_path, local_path)

  def reset_recipe_state(self):
    self.plc.write(('i_Recipes_State', 1))