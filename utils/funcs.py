import shutil
from pathlib import Path

def copytree(src: Path, folder: Path, include=tuple()):
    """
        Alternative implementation of copy tree, 
        accepts existing directory (Included by default in Python 3.8+).
        also adds an Include tuple, to only include given extensions
    """

    if not folder.exists():
        folder.mkdir(mode=0o775, exist_ok=True, parents=True)

    item: Path
    for item in src.iterdir():
        if item.is_dir():
            copytree(item, folder / item.name, include=include)
        else:
            if include and item.suffix not in include:
                continue
            shutil.copy2(item, folder)
