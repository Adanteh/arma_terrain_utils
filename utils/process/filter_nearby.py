"""
    Uses cKDTree for nearest neighbor lookup, allowing you to filter out objects close to 
    eachother and do something with it

"""

import sys
from pathlib import Path
from typing import Tuple

from pandas import DataFrame
from scipy import spatial
from gooey import Gooey, GooeyParser

FOLDER = Path(__file__).parents[2]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

from utils.tb import load_tb, write_tb, TbRow  # noqa: E402


FOLDER = Path(__file__).parent


class NearbyFiltering:
    RADIUS = 4
    DESCRIPTION = (
        "Allows you to automatically delete objects in a file, when they are closer than X distance to another file"
    )
    NAME = "Filter nearby"

    def __init__(self, radius: float, source: DataFrame, target: DataFrame):
        self.r = radius
        self.source = source
        self.target = target
        self.tree = self.create_tree(self.source)

    def create_tree(self, df: DataFrame):
        tree = spatial.cKDTree(df[["x", "y"]].values)
        return tree

    def filter_new(self):
        df = self.target
        remove_idx = []
        row: TbRow
        for idx, row in df.iterrows():
            nearby = self.filter_nearby_points([row.x, row.y], self.RADIUS)
            if nearby:
                remove_idx.append(idx)

        out = df.drop(remove_idx)
        return out

    def filter_nearby_points(self, point: Tuple[float], radius: float):
        """Cleans up all the points within X radius of current point"""

        nearby = self.tree.query_ball_point(point, radius)
        return nearby

    @classmethod
    def parser(cls, parent=None):
        if parent is None:
            parser = GooeyParser(description=cls.DESCRIPTION)
        else:
            parser = parent.add_parser(cls.NAME, help=cls.DESCRIPTION)
        parser.add_argument(
            "source", help="The TB file you want to compare distances to", type=Path, widget="FileChooser"
        )
        parser.add_argument("target", help="The file you want to filter", type=Path, widget="FileChooser")
        parser.add_argument("-r", "--radius", help="Radius", type=float, default=4)
        return parser

    @classmethod
    def run(cls, args):
        source = load_tb(args.source)
        target = load_tb(args.target)

        obj = cls(args.radius, source=source, target=args.target)
        out = obj.filter_new()

        outpath = args.target.with_name(args.target.stem + "_OUT.txt")
        write_tb(outpath, out)


if __name__ == "__main__":

    @Gooey
    def cli():
        parser = NearbyFiltering.parser()
        NearbyFiltering.run(parser.parse_args())

    cli()
