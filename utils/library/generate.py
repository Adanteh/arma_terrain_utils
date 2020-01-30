"""
Used to split up a TB library with all .p3ds into matching folder structure

py -m utils.library.generate "P:\a3" "P:\\ca" "P:\\CUP\\Terrains" "P:\\ibr" "P:\\de1"
py -m utils.library.generate "Q:\\dz" --workdrive "Q:\"
"""

import argparse
from typing import Dict, List
from datetime import datetime
from collections import defaultdict
from pathlib import Path

from gooey import Gooey
import xmltodict

from . import print
from .lib import ModelEntry
from .folders import folderWalk 


class folderToLibrary:
    tml_file: dict
    tml_entry: dict

    def __init__(self, args):
        self.args = args
        self.load_template_library()
        self.template_all = defaultdict(lambda: 0)
        self.categories = defaultdict(list)
        self.duplicates = 0

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
            self.categories[category] += entry

    def create_libraries(self, categories: Dict[str, List[ModelEntry]]):
        """Creates the library files for each category"""

        for category, entries in self.categories.items():
            print(f"<g>Creating new library {category}")

            path = Path.cwd() / "Library" / f"{category}.tml"
            parsed = self.create_category_library(category, entries)
            with path.open(mode="w") as fp:
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

        entry = self.tml_entry.copy()
        uniquename = self.handle_uniqueness(entry.name)

        entry["Name"] = uniquename
        entry["File"] = entry.relative_path
        entry["Fill"] = entry.fill
        entry["Outline"] = entry.outline
        return entry

    def handle_uniqueness(self, name: str) -> str:
        """Prevents duplicate templates appearing"""

        if self.template_all[name.lower()] == 1:
            self.duplicates += 1

            nametemp = name.lower()
            index = 1
            while self.template_all[nametemp] == 1:
                nametemp = f"{name.lower()}_{index}"
                index += 1
            name = nametemp
        self.template_all[name.lower()] = 1
        return name

    def final(self):
        """Checks if there was any weird behavior in the script"""
        if self.duplicates > 0:
            print(f"<error>Found {self.duplicates} duplicate model names, they are autorenamed</error>")
            print(
                "<error>This can cause model switching due to the nature of TB and some object placement mods (xcam, e2tb)</error>"
            )
            print(
                "<error>Use the objectPlacement mods including these new generated templates or dealwithit.jpg</error>"
            )

        print(f"<e>Completed the script with {len(self.template_all)} models processed</e>")

@Gooey
def cli():
    parser = argparse.ArgumentParser(description="TML Generation Script")
    parser.add_argument("path", help="Path to walk through")
    parser.add_argument(
        "--root", help="Workdrive path\n(This should be a parent of the base path!)", required=False, default="P:\\"
    )
    parser.add_argument(
        "--blacklist",
        help="Ignore folder names containing entries in this list\n"
        "This list is pretty decent by default, only for pro users",
        nargs="+",
        required=False,
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = cli()
    try:
        splitter = folderToLibrary(args)
    except KeyboardInterrupt:
        print("<error>The process was interrupted by the keyboard</error>")

    splitter.final()
