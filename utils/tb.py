from pathlib import Path
from dataclasses import dataclass, astuple
from typing import Generator


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

    def as_line(self) -> str:
        """Properly formatted line for a TB file"""
        values = list(self)
        values[0] = f'"{values[0]}"'  # Quotes around the model
        return ";".join((str(f) for f in values)) + self.end

    @classmethod
    def from_line(cls, line: str) -> "TbRow":
        """Creates TB entry from line in a TB file"""
        values = line.strip("\n").replace('"', "").split(";")
        return cls(*values)

    def __iter__(self):
        return iter(astuple(self)[:-1])


def tb_iterator(path: Path) -> Generator[TbRow, None, None]:
    """Loads in an object file, and yields `TbRow` objects"""
    with path.open(mode="r") as fp:
        for line in fp:
            yield TbRow.from_line(line)


from csv import QUOTE_NONE, QUOTE_NONNUMERIC  # noqa: F401, E402
import pandas as pd  # noqa: E402
from pandas import DataFrame  # noqa: E402


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
