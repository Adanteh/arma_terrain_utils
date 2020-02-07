"""
    Uses a random offset on each item, not filtered!
"""

import sys
from pathlib import Path
from random import uniform
from functools import partial

from pandas import DataFrame
from gooey import Gooey, GooeyParser


FOLDER = Path(__file__).parents[2]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

from utils.tb import load_tb, write_tb, TbRow  # noqa: E402


def action(df: DataFrame, args) -> DataFrame:
    def randomize(column: str, size: float, idx, row):
        df.at[idx, column] = row[column] + uniform(-size, size)

    def offset(column: str, _offset: float, idx, row):
        df.at[idx, column] = row[column] + _offset

    callbacks = []

    # Randomness
    for column, arg in (
        ("z", "height_random"),
        ("dir", "dir_random"),
        ("scale", "scale_random"),
        ("pitch", "pitch_random"),
    ):
        if getattr(args, arg, 0.0) != 0.0:
            callbacks.append(partial(randomize, column, getattr(args, arg, 0.0)))

    # Offset
    for column, arg in (
        ("x", "x_offset"),
        ("y", "y_offset"),
        ("z", "z_offset"),
    ):
        if getattr(args, arg, 0.0) != 0.0:
            callbacks.append(partial(offset, column, getattr(args, arg, 0.0)))

    row: TbRow
    for idx, row in df.iterrows():
        [cb(idx, row) for cb in callbacks]

    return df


class RandomOffset:
    DESCRIPTION = "Adds random offset for each line in a TB file"
    NAME = "(Random) offset"

    @classmethod
    def parser(cls, parent=None):
        if parent is None:
            parser = GooeyParser(description=cls.DESCRIPTION)
        else:
            sub = parent.add_parser(cls.__name__)
            parser = sub.add_argument_group(cls.NAME, description=cls.DESCRIPTION, gooey_options={"show_border": True})

        parser.add_argument("source", help="Input TB file", widget="FileChooser", type=Path)

        # Randomness
        random_group = parser.add_argument_group("Random", "Modify value with random value")
        random_group.add_argument("-dir", "--dir_random", help="Direction randomness", type=float, default=0.0)
        random_group.add_argument("-p", "--pitch_random", help="Pitch, bank randomness", type=float, default=0.0)
        random_group.add_argument("-zr", "--height_random", help="Height randomness", type=float, default=0.0)
        random_group.add_argument("-s", "--scale_random", help="Scale randomness", type=float, default=0.0)

        # Offset
        offset_group = parser.add_argument_group("Offset", "Change position of object")
        offset_group.add_argument("-x", "--x_offset", help="X offset", type=float, default=0.0)
        offset_group.add_argument("-y", "--y_offset", help="Y offset", type=float, default=0.0)
        offset_group.add_argument("-z", "--z_offset", help="Height offset", type=float, default=0.0)

        return parser

    @classmethod
    def run(cls, args):
        if hasattr(args, "command") and args.command != cls.__name__:
            return

        df = load_tb(args.source)
        df_out = action(df=df, args=args)
        outpath = args.source.with_name(args.source.stem + "_OUT.txt")
        write_tb(outpath, df_out)


if __name__ == "__main__":

    @Gooey
    def cli():
        parser = RandomOffset.parser()
        RandomOffset.run(parser.parse_args())

    cli()
