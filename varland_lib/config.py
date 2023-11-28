import yaml
import os

class Config:
    
    CONFIG_PATH = 'config/config.yaml'
    
    def __init__(self):
        self._load_config()

    def _load_config(self):
        with open(f"{os.getenv('LOCAL_PROJECT_PATH')}{self.CONFIG_PATH}", 'r') as file:
            self.config = yaml.safe_load(file)

    def get(self, key):
        return self.config.get(key)