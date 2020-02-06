from pathlib import Path
from dataclasses import dataclass
from typing import List, Union, Tuple
from collections import OrderedDict

import xmltodict


def dict_keys_lower(iterable: Union[OrderedDict, dict, list]):
    """Renames all key in orderdeddict recursively to lowercase"""
    newdict = type(iterable)()
    if type(iterable) in (dict, OrderedDict):
        for key in iterable.keys():
            newdict[key.lower()] = iterable[key]
            if type(iterable[key]) in (dict, list, OrderedDict):
                newdict[key.lower()] = dict_keys_lower(iterable[key])
    elif type(iterable) is list:
        for item in iterable:
            item = dict_keys_lower(item)
            newdict.append(item)
    else:
        return iterable
    return newdict


def tbcolor_to_hex(number: int) -> "str":
    """Converts inverted hexidemical to a normal hex color code"""
    uninverted_decimal = number - int("0xffffff", 16)
    hexed = hex(uninverted_decimal).split("x")[-1]
    table = "ok".maketrans("0123456789abcdef", "fedcba9876543210")
    inverted = "#" + hexed[1:].lower().translate(table).upper()
    return inverted


def tbcolor_to_rgba(number: int, alpha=255) -> Tuple[int]:
    """Converts weird tb color format to 255 rgba"""
    hex_color = tbcolor_to_hex(number)[1:]
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return (*rgb, alpha)


@dataclass
class ModelEntry:
    name: str
    file: str
    fill: int
    outline: int
    landslope: bool = False
    size: Tuple[float] = (1.0, 1.0, 1.0)

    @classmethod
    def from_library(cls, values: dict) -> "ModelEntry":
        values = dict_keys_lower(values)
        return cls(
            values["name"],
            values["file"],
            int(values["fill"]),
            int(values["outline"]),
            values["placement"] == "slopelandcontact",
            size=cls.handle_size(values),
        )

    @staticmethod
    def handle_size(values: dict) -> Tuple[float]:
        x_max, y_max, z_max = (float(f) for f in values["boundingmax"].values())
        x_min, y_min, z_min = (float(f) for f in values["boundingmin"].values())
        return (x_max - x_min, y_max - y_min, z_max - z_min)

    def as_shape(self):
        """Returns as (`name`, `rgba_fill`, `rgba_outline`, `size`)"""
        return (self.name, tbcolor_to_rgba(self.fill), tbcolor_to_rgba(self.outline), self.size)


class TbLibraryCollection:
    def __init__(self, folder: Path):
        self.libraries: List[TbLibrary] = self.load_libraries(folder)
        self._lib, self._entries = self.cache(self.libraries)

    def load_libraries(self, folder: Path):
        libraries = []
        for tml_file in folder.glob("*.tml"):
            libraries.append(TbLibrary.from_file(tml_file))
        return libraries

    def cache(self, libraries):
        _lib_cache = {}
        _entry_cache = {}
        for lib in libraries:
            for entry in lib:
                _lib_cache[entry.name.lower()] = lib.name
                _entry_cache[entry.name.lower()] = entry
        return _lib_cache, _entry_cache

    def __iter__(self):
        for i in self.libraries:
            yield i

    def get_category(self, name: str) -> str:
        """Gets the library name from model"""
        return self._lib[name.lower()]

    def get_entry(self, name: str) -> ModelEntry:
        """Gets the ModelEntry from model"""
        return self._entries[name.lower()]

    def __getitem__(self, key: str):
        return self.get_entry(key)


class TbLibrary:
    """This represents a single .tml file"""

    def __init__(self, library: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)

        entries = self.__fix(library)
        self._dict = library  # Unedited xmldict
        self.entries: List[ModelEntry] = [ModelEntry.from_library(entry) for entry in entries]
        self.name = library["Library"]["@name"]
        self.shape = library["Library"]["@shape"]

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
        for i in self.entries:
            yield i
