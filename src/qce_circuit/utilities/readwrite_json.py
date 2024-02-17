# -------------------------------------------
# Functions for import/export and formatting json.
# -------------------------------------------
import os
import json
from typing import Union
from pathlib import Path
from qce_circuit.definitions import ROOT_DIR

JSON_ROOT = ROOT_DIR


# --- JSON Read/Write  ---

def get_json_file_path(filename: str) -> Path:
    """Returns json file path as used by read/write functions."""
    return Path(os.path.join(JSON_ROOT, filename))


def read_json(filename: str) -> Union[dict, FileNotFoundError]:
    """Returns json after importing from JSON_ROOT + filename."""
    file_path = get_json_file_path(filename=filename)
    # Check if filename is already an absolute file path
    absolute_path: bool = os.path.isabs(filename)
    print('is absolute file path: ', filename, absolute_path)
    if absolute_path:
        file_path = filename
    
    with open(file_path) as f:
        config = json.load(f)
    return config

def write_json(filename: str, packable: dict, make_file: bool = False, *args, **kwargs) -> bool:
    """Returns if file exists. Dumps config_dict to json file."""
    # Dump dictionary into yaml file
    file_path = get_json_file_path(filename=filename)
    if not make_file and not os.path.isfile(file_path):
        return False
    with open(file_path, 'w') as f:
        json.dump(packable, f, indent=4, *args, **kwargs)
    return True
