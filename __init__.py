import importlib
import inspect
import json
import subprocess
from pathlib import Path

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

config = {
    "Settings": {
        "Install Requirements": False,
        "Update Repository": False,
        "Quiet Update": True,
    },
    "Load Nodes": {
        "Aesthetic": True,
        "IF": True,
        "Image": True,
        "Multi": True,
        "Text": True,
    },
}

path = Path(__file__)
git_path = path.parent
config_path = path.with_name("config.json")
req_path = path.with_name("requirements.txt")
first_run = False

if config_path.is_file():
    try:
        with open(config_path, "r") as f:
            try:
                dict = json.load(f)

                for key, value in dict.items():
                    if key in config:
                        for k, v in value.items():
                            if k in config[key]:
                                config[key][k] = v
            except:
                print("[\033[94mZuellni\033[0m]: Invalid config. Loading defaults...")
    except:
        print("[\033[94mZuellni\033[0m]: Couldn't open config. Loading defaults...")
else:
    first_run = True

try:
    with open(config_path, "w") as f:
        json.dump(config, f, indent="\t", separators=(",", ": "))
except:
    print("[\033[94mZuellni\033[0m]: Couldn't save config. Proceeding...")

quiet = ["-q"] if config["Settings"]["Quiet Update"] else []

if config["Settings"]["Update Repository"]:
    print("[\033[94mZuellni\033[0m]: Updating repository...")
    subprocess.run(["git", "-C", git_path, "pull"] + quiet)

if config["Settings"]["Install Requirements"] or first_run:
    print("[\033[94mZuellni\033[0m]: Installing requirements...")
    subprocess.run(["python", "-m", "pip", "install", "-U", "-r", req_path] + quiet)

for key, value in config["Load Nodes"].items():
    if value:
        module = importlib.import_module(f".Nodes.{key}", package=__name__)

        for name, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ == module.__name__:
                key = key.replace("_", " ")
                name = name.replace("_", " ")

                node = f"Zuellni {key} {name}"
                disp = f"{key} {name}"

                NODE_CLASS_MAPPINGS[node] = cls
                NODE_DISPLAY_NAME_MAPPINGS[node] = disp