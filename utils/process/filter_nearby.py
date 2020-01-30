"""
    Uses cKDTree for nearest neighbor lookup, allowing you to filter out objects close to 
    eachother and do something with it

"""

import argparse
from pathlib import Path
from typing import Tuple

from pandas import DataFrame
from scipy import spatial

from ..tb import load_tb, write_tb

FOLDER = Path(__file__).parent


class NearbyFiltering:
    RADIUS = 4

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

    def do_stuff(self, point):
        print(point)


def main(args):
    target_path = Path(args.target[0])
    source = load_tb(Path(args.source[0]))
    target = load_tb(target_path)

    obj = NearbyFiltering(args.r, source=source, target=target)
    out = obj.filter_new()

    outpath = target_path.with_name(target_path.stem + "_OUT.txt")
    write_tb(outpath, out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="The TB file you want to compare distances to", nargs=1)
    parser.add_argument("target", help="The file you want to filter", nargs=1)
    parser.add_argument("-r", help="Radius", type=float, default=4)
    args = parser.parse_args()

    main(args)
