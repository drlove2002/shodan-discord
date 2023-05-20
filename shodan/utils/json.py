import json
from pathlib import Path

__all__ = ["read_json", "write_json", "unset_json", "upsert_json"]

from typing import List, Dict, Union, Any, Optional


def get_path():
    """
    A function to get the current path to bot.py
    Returns:
     - cwd (string) : Path to bot.py directory
    """
    cwd = Path(__file__).parents[1]
    cwd = str(cwd)
    return cwd


def read_json(filename) -> Optional[Union[Dict, List]]:
    """
    A function to read a json file and return the data.
    Params:
     - filename (string) : The name of the file to open
    Returns:
     - data (dict) : A dict of the data in the file
    """
    cwd = get_path()
    try:
        with open(cwd + "/assets/" + filename + ".json", "r", encoding="utf8") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = None
    return data


def write_json(data: Dict[str, Union[str, int, List[Any], Dict[Any, Any]]], filename):
    """
    A function used to write data to a json file
    Params:
     - data (dict) : The data to write to the file
     - filename (string) : The name of the file to write to
    """
    cwd = get_path()
    with open(cwd + "/assets/" + filename + ".json", "w", encoding="utf8") as file:
        json.dump(data, file, indent=4)


def unset_json(data: List[str], filename):
    """A function to remove a value from a json file"""
    json_data = read_json(filename)
    for value in data:
        if json_data and value in json_data:
            json_data.pop(value)
    write_json(json_data, filename)


def upsert_json(data: Dict[str, Union[str, int, List[Any], Dict[Any, Any]]], filename):
    """A function to update a json file"""
    config = read_json(filename)
    if config:
        for key, value in data.items():
            config[key] = value
    else:
        config = data
    write_json(config, filename)
