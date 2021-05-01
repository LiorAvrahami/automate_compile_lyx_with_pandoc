from pathlib import Path
import os.path
import sys

def run(func,root_path,b_recursive=False,files_filter = "*",b_yield_folders=False):
    root_path = Path(root_path)
    if root_path.is_dir():
        if b_recursive:
            paths = list(root_path.rglob(files_filter))
        else:
            paths = list(root_path.glob(files_filter))
    else:
        if root_path in list(root_path.parent.glob(files_filter)):
            paths = [root_path]
        else:
            return
    for path in paths:
        if b_yield_folders or not path.is_dir():
            func(path)
