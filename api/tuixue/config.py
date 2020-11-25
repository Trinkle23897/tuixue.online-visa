import os
import json
from datetime import datetime

def load_config():
    global config
    with open("config.json", "r") as f:
        config = json.load(f)
    return datetime.now()

config = {}
last_update = load_config()

def get(item):
    global config, last_update
    current_time = datetime.now()
    if (current_time - last_update).total_seconds() > 180:
        last_update = load_config()
    return config.get(item)
