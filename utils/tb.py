from csv import QUOTE_NONE, QUOTE_NONNUMERIC  # noqa: F401
from pathlib import Path
from dataclasses import dataclass

import pandas as pd
from pandas import DataFrame


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
