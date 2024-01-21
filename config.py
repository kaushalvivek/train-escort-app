'''
Read config from config.yaml file and make it available to other modules
'''
import yaml

CONFIG_FILE = 'config.yaml'

class AppConfig:
    def __init__(self):
        with open(CONFIG_FILE, 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
    
    def get_config(self):
        return self.config['app']