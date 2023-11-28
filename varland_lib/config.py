import yaml

class Config:
    
    CONFIG_PATH = '/Users/varland/Desktop/vppython/config/config.yaml'
    
    def __init__(self):
        self._load_config()

    def _load_config(self):
        with open(self.CONFIG_PATH, 'r') as file:
            self.config = yaml.safe_load(file)

    def get(self, key):
        return self.config.get(key)