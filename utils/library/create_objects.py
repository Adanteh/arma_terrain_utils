import argparse
import xmltodict
from typing import List
from pathlib import Path

from .lib import TbLibrary, ModelEntry
from ..tb import TbRow


def cli():
    parser = argparse.ArgumentParser(description="TML Generation Script")
    parser.add_argument("library", help="Path to walk through")
    return parser.parse_args()


class CreateObjects:
    def __init__(self, args):
        self.x = 0
        self.y = 0
        self.libaries = self.load_library(Path(args.library))

    def load_library(self, library: Path):
        libraries = []
        for tml_file in library.glob("**.tml"):
            libraries.append(TbLibrary.from_file(tml_file))
        return libraries

    def iteration(self):
        for lib in self.libaries:
            model: ModelEntry
            for model in lib:
                TbRow(model.name)


if __name__ == "__main__":
    args = cli()
    obj = CreateObjects(args)
    obj.main(args)
