import sys
from pathlib import Path

from gooey import Gooey, GooeyParser

FOLDER = Path(__file__).parents[2]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

FILE: Path = Path(__file__).parent / ".tml_selected.txt"


class TmlFilter:
    """Allows you to filter based on TML entries"""

    DESCRIPTION = "Limits actions of TB tools to only work on models within one of these libraries"
    NAME = "Filter"

    @classmethod
    def parser(cls, parser=None):
        choices = cls.load_files()
        parser.add_argument(
            "filter",
            help="Something",
            widget="Listbox",
            choices=choices,
            nargs="*",
            default=cls.load_selected(choices),
            gooey_options={"height": 220},
        )
        return parser

    @classmethod
    def run(cls, args):
        cls.save_selected(args)
        return args.filter

    @staticmethod
    def load_files():
        return [file.stem for file in (FOLDER / "Library").glob("*.tml")]

    @staticmethod
    def save_selected(args):
        with FILE.open(mode="w") as fp:
            [fp.write(arg + "\n") for arg in args.filter]

    @staticmethod
    def load_selected(possible) -> tuple:
        if not FILE.exists():
            return tuple()

        selected = []
        with FILE.open(mode="r") as fp:
            for line in fp:
                line = line.strip("\n")
                if line in possible:
                    selected.append(line)

        return tuple(selected)


if __name__ == "__main__":

    @Gooey
    def cli():
        parser = TmlFilter.parser()
        TmlFilter.run(parser.parse_args())

    cli()
