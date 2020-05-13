from pathlib import Path
from dataclasses import dataclass
from typing import List, Union, Tuple, Dict, Optional
from collections import OrderedDict

import ctypes
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


def get_v4_hash(name: str) -> int:
    """Creates the hash required for TB, given `name` (template name)"""
    _hash = 0
    for letter in name:
        _hash = (ord(letter) + (_hash << 6) + (_hash << 16) - _hash) & 0xFFFFFFFF
    return ctypes.c_long(_hash).value


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

    def __iter__(self) -> "TbLibrary":
        for i in self.libraries:
            yield i

    def get_category(self, name: str) -> str:
        """Gets the library name from model"""
        return self._lib[name.lower()]

    def get_entry(self, name: str) -> Union[ModelEntry, None]:
        """Gets the ModelEntry from model"""
        try:
            return self._entries[name.lower()]
        except KeyError:
            return None

    def __getitem__(self, key: str):
        return self.get_entry(key)


class TbLibrary:
    """This represents a single .tml file"""

    def __init__(self, library: dict, *args, path=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.__fix(library)
        self._dict = library  # Unedited xmldict
        self._dictlower: Dict[str, OrderedDict] = {}

        self.entries: Dict[str, ModelEntry] = {}
        for entry in library["Library"]["Template"]:
            model = ModelEntry.from_library(entry)
            self.entries[model.name] = model
            self._dictlower[model.name.lower()] = entry

        self.path = path

    @property
    def name(self):
        return self._dict["Library"]["@name"]

    @property
    def shape(self):
        return self._dict["Library"]["@shape"]

    @classmethod
    def from_file(cls, path: Path) -> "TbLibrary":
        """Creates a library from a file directly"""
        if not path.exists():
            raise FileNotFoundError

        with path.open(mode="r") as fp:
            library = xmltodict.parse(fp.read())
        return cls(library, path=path)

    def save(self, path: Union[Path, None] = None):
        """Write the dict back to a file. If `path` is not given it'll use the path is was opened with (If available)"""
        if path is None:
            path = self.path
            if path is None:
                raise Exception(f"No path given to save {self}")

        with path.open(mode="w") as fp:
            xmltodict.unparse(self._dict, output=fp, pretty=True)

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
        library["Library"]["Template"] = entries

    def __len__(self):
        return len(self.entries)

    def __str__(self):
        return self.name

    def __iter__(self) -> OrderedDict:
        for i in self.entries.values():
            yield i

    def __getitem__(self, key: str) -> OrderedDict:
        _dict_lower = {k.lower(): v for k, v in self._dictlower.items()}
        return _dict_lower[key.lower()]


class TbObject:
    """Object with all data a terrain builder object holds"""

    version = "0.1"

    def __init__(
        self,
        classname: str,
        position: Optional[List[int]] = [0, 0, 0],
        rotation: Optional[List[int]] = [0, 0, 0],
        scale: float = 1,
    ):
        r"""
            args:
            classname (str): template/modelname
            [position] (list): x, y, z position (z being above sea level)
            [rotation] (list): pitch, bank, yaw
            [scale] (int): scale
        """
        self.classname = classname.strip('"')  # Remove double quotes
        self.position = position
        self.rotation = rotation
        self.scale = scale

    def __repr__(self):
        return "{}({} at pos {self.position_round()})".format(self.__class__.__name__, self.classname)

    def __str__(self):
        return self.classname

    def position_round(self) -> list:
        """Gets x, y coordinates in full meters"""
        return [round(f, 0) for f in self.position[:2]]

    @classmethod
    def from_tb_format(cls, line: str):
        """Constructs a tb object from a import/export line"""
        data = line.split(";")
        datafloat = [float(f) for f in data[1:8]]
        datafloat.insert(0, data[0])
        position = [datafloat[1], datafloat[2], datafloat[7]]
        rotation = [datafloat[4], datafloat[5], datafloat[3]]
        return cls(data[0], position, rotation, float(data[6]))

    def tb_format(self) -> str:
        """Gets export/import line in TB format"""
        return (
            ";".join(
                str(x)
                for x in (
                    '"' + self.classname + '"',
                    self.position[0],  # X
                    self.position[1],  # Y
                    self.rotation[2],  # Yaw
                    self.rotation[0],  # Pitch
                    self.rotation[1],  # Bank
                    self.scale,
                    self.position[2],
                )
            )
            + ";"
        )


def tb_split_simple(line: str) -> List[List[str]]:
    """Simple splitting of data in TB format"""
    cleaned = line.strip("\n")
    if cleaned.endswith(";"):
        cleaned = cleaned[:-1]
    return cleaned.split(";")
