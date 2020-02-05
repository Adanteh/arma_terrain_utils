import sys
from pathlib import Path

from gooey import Gooey, GooeyParser

FOLDER = Path(__file__).parents[2]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

from utils.tb import TbLibrary, ModelEntry, TbRow  # noqa: E402


class CreateObjects:
    DESCRIPTION = "Creates an object for every single entry in library files"
    NAME = "create"
    LOCATION_OFFSET = (200000.0, 0.0)

    @classmethod
    def parser(cls, parent=None):
        if parent is None:
            parser = GooeyParser(description=cls.DESCRIPTION)
        else:
            parser = parent.add_parser(cls.NAME, help=cls.DESCRIPTION)
        parser.add_argument("library", help="Path to walk through", widget="DirChooser")
        parser.add_argument(
            "-o",
            "--output",
            help="Path to walk through",
            widget="FileSaver",
            type=Path,
            default=str(Path.cwd() / "tb_all_objects.txt"),
        )
        parser.add_argument("-s", "--spacing", type=float, help="Distance between items", default=25.0)
        return parser

    @classmethod
    def run(cls, args):
        if not hasattr(args, "command") or args.command == cls.NAME:
            obj = cls(args)
            obj.create_objects()

    def __init__(self, args):
        self.x, self.y = self.LOCATION_OFFSET
        self.args = args
        self.libaries = self.load_library(Path(args.library))

    def create_objects(self):
        with self.args.output.open(mode="w") as fp:
            entry: TbRow
            for entry in self.iteration(self.args.spacing):
                fp.write(entry.as_line() + "\n")

    def load_library(self, library: Path):
        libraries = []
        for tml_file in library.glob("*.tml"):
            libraries.append(TbLibrary.from_file(tml_file))
        return libraries

    def iteration(self, spacing: int):
        for lib in self.libaries:
            model: ModelEntry
            self.y = self.LOCATION_OFFSET[1] + spacing
            self.x += spacing

            for model in lib:
                self.y += spacing
                yield TbRow(model.name, x=self.x, y=self.y)


if __name__ == "__main__":

    @Gooey
    def cli():
        parser = CreateObjects.parser()
        CreateObjects.run(parser.parse_args())

    cli()
