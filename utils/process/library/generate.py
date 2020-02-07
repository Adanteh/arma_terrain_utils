"""
Used to split up a TB library with all .p3ds into matching folder structure

py -m utils.library.generate "P:\a3" "P:\\ca" "P:\\CUP\\Terrains" "P:\\ibr" "P:\\de1"
py -m utils.library.generate "Q:\\dz" --workdrive "Q:\"
"""

import sys
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
from pathlib import Path

import xmltodict
from gooey import Gooey, GooeyParser

FOLDER = Path(__file__).parents[2]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

from utils import print  # noqa: E402
from utils.library import ModelEntry  # noqa: E402
from utils.process.library.folders import folderWalk, BLACKLIST  # noqa: E402


class folderToLibrary:
    """
        Processes libraries. Call order is:
            `walk_folder`
            `folderWalk.walk_folders`
            `create_libraries`
            `create_category_library`
            `set_template_data`

    """

    tml_file: dict
    tml_entry: dict

    def __init__(self, args):
        self.args = args
        self.load_template_library()
        self.template_all = defaultdict(lambda: 0)
        self.categories = defaultdict(list)
        self.duplicates = []

        self.output = args.output
        self.output.mkdir(mode=0o775, parents=True, exist_ok=True)

        self.walk_folder()
        self.create_libraries(self.categories)

    def load_template_library(self):
        """Load in the default library format"""
        default_template = Path(__file__).parent / "data" / "empty_template.tml"
        with default_template.open(mode="r") as library_file:
            self.tml_file = xmltodict.parse(library_file.read())
            self.tml_entry = self.tml_file["Library"]["Template"][0]
            self.tml_entry["Date"] = str(datetime.now())

    def walk_folder(self):
        walk = folderWalk(self.args.path, self.args.blacklist, root=self.args.root)
        for category, entry in walk.walk_folders():
            self.categories[category].append(entry)

    def create_libraries(self, categories: Dict[str, List[ModelEntry]]):
        """Creates the library files for each category"""

        for category, entries in self.categories.items():
            print(f"<g>Creating new library {category}")

            output = self.output / f"{category}.tml"
            parsed = self.create_category_library(category, entries)
            with output.open(mode="w") as fp:
                fp.write(xmltodict.unparse(parsed, pretty=True))

    def create_category_library(self, category: str, entries: List[ModelEntry]) -> dict:
        """
            Creates a new library dict for a category, and copies over all the info 
            that matches these models fromt the source dictionary
        """

        library = self.tml_file.copy()
        library["Library"]["@name"] = category

        entries_dict = [self.set_template_data(f) for f in entries]
        library["Library"]["Template"] = entries_dict
        return library

    def set_template_data(self, entry: ModelEntry) -> dict:
        """Sets the data to a template entry in the dictionary"""

        tml_base = self.tml_entry.copy()
        uniquename = self.handle_uniqueness(entry.name)

        tml_base["Name"] = uniquename
        tml_base["File"] = entry.file
        tml_base["Fill"] = entry.fill
        tml_base["Outline"] = entry.outline
        return tml_base

    def handle_uniqueness(self, name: str) -> str:
        """Prevents duplicate templates appearing"""

        if self.template_all[name.lower()]:

            nametemp = name.lower()
            index = 1
            while self.template_all[nametemp]:
                nametemp = f"{name.lower()}_{index}"
                index += 1
            name = nametemp
            self.duplicates.append(nametemp)

        self.template_all[name.lower()] = 1
        return name

    def final(self):
        """Checks if there was any weird behavior in the script"""
        if self.duplicates:
            self._write_duplicates()

        print(f"<e>Completed the script with {len(self.template_all)} models processed</e>")

    def _write_duplicates(self):
        print(f"<error>Found {len(self.duplicates)} duplicate model names, they are autorenamed</error>")
        print("This can cause model switching due to the nature of TB and some object placement mods (xcam, e2tb)")

        output: Path = self.output / "# duplicates.txt"

        print(f"<error>Wrote duplicate names to {output}")

        with output.open(mode="w") as fp:
            for dup in self.duplicates:
                fp.write(dup + "\n")


def main(args):
    try:
        splitter = folderToLibrary(args)
    except KeyboardInterrupt:
        print("The process was interrupted by the keyboard</error>")

    splitter.final()


class Generate:
    DESCRIPTION = "Generates Terrain Builder template files from walking through folders"
    NAME = "Create library"

    @classmethod
    def parser(cls, parent=None):
        if parent is None:
            parser = GooeyParser(description=cls.DESCRIPTION)
        else:
            parser = parent.add_parser(cls.NAME, help=cls.DESCRIPTION)

        parser.add_argument("--path", help="Path to walk through", widget="DirChooser", default="P:/a3", type=Path)
        parser.add_argument(
            "--root",
            help="Workdrive path\n(This should be a parent of the base path!)",
            required=False,
            default="P:/",
            widget="DirChooser",
            type=Path,
        )
        parser.add_argument(
            "--blacklist",
            help="Ignore folder names containing entries in this list\n"
            "This list is pretty decent by default, only for pro users",
            nargs="+",
            default=" ".join(BLACKLIST),
            required=False,
        )
        parser.add_argument(
            "-o",
            "--output",
            help="Where to create the library",
            default=str(Path.cwd() / "Library"),
            type=Path,
            widget="DirChooser",
        )

        return parser

    @classmethod
    def run(cls, args):
        if not hasattr(args, "command") or args.command == cls.NAME:
            main(args)


if __name__ == "__main__":

    @Gooey
    def cli():
        parser = Generate.parser()
        Generate.run(parser.parse_args())

    cli()
