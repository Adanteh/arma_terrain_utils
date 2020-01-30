"""
    Uses a random offset on each item, not filtered!
"""

from pathlib import Path
from random import uniform
from pandas import DataFrame
import argparse

from ..tb import load_tb, write_tb, TbRow

FOLDER = Path(__file__).parent


def action(df: DataFrame, **kwargs) -> DataFrame:
    min_, max_ = (kwargs["offset"] * -1, kwargs["offset"])

    row: TbRow
    for idx, row in df.iterrows():
        df.at[idx, "z"] = row["z"] + uniform(min_, max_)
    return df


def handle_file(file: Path):
    file = Path(args.source[0])
    df = load_tb(file)
    df_out = action(df, offset=args.offset)
    outpath = file.with_name(file.stem + "_OUT.txt")
    write_tb(outpath, df_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="The TB file you want to compare distances to", nargs=1)
    parser.add_argument("-o", "--offset", help="Offset", type=float, default=0.1)
    args = parser.parse_args()

    handle_file(args)
