from csv import QUOTE_NONE, QUOTE_NONNUMERIC  # noqa: F401
from pathlib import Path
from dataclasses import dataclass, astuple
from typing import List

import xmltodict
import pandas as pd
from pandas import DataFrame

from utils.misc import dict_keys_lower

NAMES = ("model", "x", "y", "dir", "pitch", "bank", "scale", "z", "end")


@dataclass
class TbRow:
    """
        Row of tb contains
        `("model", "x", "y", "dir", "pitch", "bank", "scale", "z", "end")`
    """

    model: str
    x: float = 0.0
    y: float = 0.0
    dir: float = 0.0
    pitch: float = 0.0
    bank: float = 0.0
    scale: float = 1.0
    z: float = 0.0
    end: str = ";"

    def as_line(self):
        """Properly formatted line for a TB file"""
        values = list(self)
        values[0] = f'"{values[0]}"'  # Quotes around the model
        return ";".join((str(f) for f in values)) + self.end

    def __iter__(self):
        return iter(astuple(self)[:-1])


@dataclass
class ModelEntry:
    name: str
    file: str
    fill: int
    outline: int
    landslope: str = False
    bounding: List[str] = None

    @classmethod
    def from_library(cls, values: dict) -> "ModelEntry":
        values = dict_keys_lower(values)
        return cls(
            values["name"],
            values["file"],
            int(values["fill"]),
            int(values["outline"]),
            values["placement"] == "slopelandcontact",
        )


def load_tb(path: Path) -> DataFrame:
    """Makes pandas DataFrame out of Terrain builder format"""
    names = NAMES

    if not path.is_file():
        raise FileNotFoundError(f"File {path} does not exist")
    df = pd.read_csv(path, delimiter=";", header=0, names=names)  # type: DataFrame
    return df


def write_tb(path: Path, df: DataFrame):
    """Makes terrain builder file out of DataFrame"""
    float_format = "%.6f"

    # Require quotes around model. In theory quoting=QUOTE_NONNUMERIC should work, but its broken for formatted floats
    df.update(df[["model"]].applymap('"{}"'.format))
    df.to_csv(path, header=False, index=False, sep=";", quoting=QUOTE_NONE, float_format=float_format)


class TbLibrary(object):
    def __init__(self, library, *args, **kwargs):
        super().__init__(*args, **kwargs)

        entries = self.__fix(library)
        self.entries: List[ModelEntry] = [ModelEntry.from_library(entry) for entry in entries]
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
        for i in self.entries:
            yield i

