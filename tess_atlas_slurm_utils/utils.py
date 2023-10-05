import os
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SLURM-UTILS")




def get_python_source_command():
    path_to_python = shutil.which("python")
    path_to_env_activate = path_to_python.replace("python", "activate")
    return f"source {path_to_env_activate}"


def to_str_list(li):
    return " ".join([str(i) for i in li])


def mkdir(base, name=None):
    if name:
        newpth = os.path.join(base, name)
        dirname = base if "." in name else newpth
    else:
        newpth = base
        dirname = base
    os.makedirs(dirname, exist_ok=True)
    return newpth
