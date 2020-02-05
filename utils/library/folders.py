from pathlib import Path
from typing import List, Generator, Tuple
from collections import defaultdict, OrderedDict

from utils import print
from utils.tb import ModelEntry
from utils.library.get_category import clean_name, get_category_custom

BLACKLIST = [
    "air",
    "weapons",
    "characters",
    "soft",
    "armor",
    "animals",
    "anim",
    "proxies",
    "particleeffects",
    "modules",
    "\\data_f",  # A3 stuff
    "curator",
    "\\boat",
    "\\static",
    "\\ui",
    "tracked",
    "wheeled",
    "proxy",  # A2 stuff from CUP
]


class keydefaultdict(defaultdict):
    """Default dict, but passes the key to our default callable"""

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            ret = self[key] = self.default_factory(key)
            return ret


class folderWalk:
    def __init__(self, target: Path, blacklist: List[str] = None, root: Path = None):
        """
            Used to walk through P drive (default) or other given item
        """
        if root is None:
            root = Path("P:/")

        if blacklist is None:
            blacklist = BLACKLIST

        self.root = root
        self.target = target
        self.clean_names = keydefaultdict(clean_name)
        self.blacklist = blacklist

    def walk_folders(self) -> Generator[Tuple[str, ModelEntry], None, None]:
        """Walks the folders below start path, checking for p3d"""

        if not self.root.exists():
            print(f"<error>The given root '{self.root}' doesn't exist</error>")
            return

        if not self.target.exists():
            print(f"<error>The given base path {self.target} does not exist</error>")
            return

        print(f"<g>Starting p3d search within path {self.target}</g>")
        for model in self.target.glob("**/*.p3d"):
            folder: Path = model.parent

            relative_path: Path = model.relative_to(self.root)
            parents = list(relative_path.parts)[:-1][:3]  # Only keep 3 parents max (Discard filename first)
            parents = [f.lower().replace("_f", "") for f in parents]  # Strip the "_f" ending

            parentsnew = list(OrderedDict.fromkeys(parents))  # Get unique (Prevent roads_roads prefix)
            prefix = "_".join(parentsnew)

            if not self.check_folder(relative_path, parents, prefix):
                continue

            name: str = model.stem
            if name in ["horizont", "obloha"]:
                continue

            category = self.clean_names[prefix]
            details = get_category_custom(relative_path)
            yield category, ModelEntry(name, str(relative_path), details.fill, details.outline)

    def check_folder(self, folder: Path, parents: list, prefix: str) -> bool:
        """Checks if this folder should be added as template"""
        # Ignore anything given in blacklist (Weapons, air, etc)

        for check in self.blacklist:
            if str(folder).lower().find(check) >= 0:
                return False

        # Skip any folder starting with underscore
        if list(filter(lambda x: x.startswith("_"), parents)):
            # print(f"<grey>found underscore in {parents}</grey>")
            return False

        return True
