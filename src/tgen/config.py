import json

from src.tgen import path


def read_config():
    with (path.resources() / "config.json").open() as f:
        return json.load(f)


def write_config(auto_run=None):
    config = read_config()
    
    if auto_run is not None:
        config["auto_run"] = auto_run
    
    with (path.resources() / "config.json").open("w") as f:
        json.dump(config, f, indent=2)
