from pathlib import Path

from utils.tb import TbLibrary, ModelEntry, TbRow


class CreateObjects:
    DESCRIPTION = "Creates an object for every single entry in library files"
    NAME = "create"

    @classmethod
    def parser(cls, parent=None):
        _parser = parent.add_parser(cls.NAME, help=cls.DESCRIPTION)
        _parser.add_argument("library", help="Path to walk through", widget="DirChooser")

    @classmethod
    def run(cls, args):
        if args.command != cls.NAME:
            return
            
        obj = cls(args)
        obj.main(args)

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
    args = CreateObjects.parser()
    CreateObjects.run(args)
