import sys
from pathlib import Path

from gooey import Gooey, GooeyParser

FOLDER = Path(__file__).parents[3]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

from utils.tb import TbRow  # noqa: E402
from utils.library import TbLibraryCollection, TbLibrary, ModelEntry  # noqa: E402


class AddData:
    DESCRIPTION = (
        "Copies over some data from one library file containing all entries, to split library\n"
    )
    NAME = "Add Library Data"

    def __init__(self, args):
        self.args = args
        self.missing = 0
        self.libaries = TbLibraryCollection(Path(args.library))
        self.source = self.load_source(args)

    @classmethod
    def parser(cls, parent=None):
        if parent is None:
            parser = GooeyParser(description=cls.DESCRIPTION)
        else:
            sub = parent.add_parser(cls.__name__)
            parser = sub.add_argument_group(cls.NAME, description=cls.DESCRIPTION, gooey_options={"show_border": True})

        parser.add_argument("library", help="Path to walk through", widget="DirChooser")
        parser.add_argument("source", help="Source library file", widget="FileChooser")
        return parser

    @classmethod
    def run(cls, args):
        if hasattr(args, "command") and args.command != cls.__name__:
            return

        obj: "AddData" = cls(args)
        obj.action()
        obj.final()

    def load_source(self, args):
        return TbLibrary.from_file(Path(args.source))

    def action(self):
        library: TbLibrary
        model: ModelEntry
        for library in self.libaries:
            print(library.name)
            for model in library:
                try:
                    _hash = self.source[model.name]["Hash"]
                    library[model.name]["Hash"] = _hash
                except KeyError:
                    self.missing += 1
                    print(f"Missing template: '{model.name}'")

            library.save()
                

    def final(self):
        print(f"Missing templates: {self.missing}")


if __name__ == "__main__":

    @Gooey
    def cli():
        parser = AddData.parser()
        AddData.run(parser.parse_args())

    cli()
