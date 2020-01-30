from typing import List
from dataclasses import dataclass
from pathlib import Path
import xmltodict

@dataclass
class ModelEntry:
    name: str
    relative_path: str
    fill: int
    outline: int
    landslope: str = False
    bounding: List[str] = None

    @classmethod
    def from_library(cls, values: dict):
        return cls(values["Name"], values["File"], values["Fill"], values["Outline"], values["Placement"])


class TbLibrary(object):
    def __init__(self, library, *args, **kwargs):
        super().__init__(*args, **kwargs)

        entries = self.__fix(library)
        self.entries: List[ModelEntry] = [ModelEntry(entry) for entry in entries]
        self.name = library["Library"]["@name"]

    @classmethod
    def from_file(cls, path: Path) -> "TbLibrary":
        """Creates a library from a file directly"""
        if not path.exists():
            raise FileNotFoundError

        with path.open(mode="r") as fp:
            library = xmltodict.parse(fp.read())
        return cls(library)

    def __fix(self, library) -> List[dict]:
        """Fixes usual discrepancies between different template files"""
        try:
            entries = library["Library"]["Template"]
            entries[0]["Name"]
        except (NameError, KeyError):
            try:
                entries = [library["Library"]["Template"]]
            except KeyError:
                entries = []
        return entries

    def __len__(self):
        return len(self.entries)

    def __str__(self):
        return self.name

    def __iter__(self):
        return self

    def __next__(self):
        for i in self.entries:
            yield i
