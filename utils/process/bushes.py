"""
    Adds a bush near every tree
"""

import argparse
from pathlib import Path
from random import uniform
from math import cos, sin

TREE = "t_Inocarpus_F"
BUSH = '"b_Leucaena_F"'
FOLDER = Path(__file__).parent


def from_tb_format(line: str) -> dict:
    """Constructs a tb object from a import/export line"""
    data = line.strip("\n").split(";")
    model = data[0]

    datafloat = [float(f) for f in data[1:8]]
    datafloat.insert(0, data[0])
    position = [datafloat[1], datafloat[2], datafloat[7]]
    rotation = [datafloat[4], datafloat[5], datafloat[3]]
    items = {"position": position, "rotation": rotation, "model": data[0].replace('"', ""), "scale": datafloat[6]}
    return items


def create_bush(data):
    pos = data["position"]
    radius = 2
    scale = round(uniform(2, 0.5), 3)
    angle = round(uniform(0, 360), 3)
    pos = (pos[0] + radius * cos(angle), pos[1] + radius * sin(angle), -0.2)
    line = ";".join(str(f) for f in [BUSH, round(pos[0], 3), round(pos[1], 3), angle, 0, 0, scale, pos[2]])
    return line + "\n"


def handle_file(file: Path):
    new_file = FOLDER / "bushes_out.txt"
    with new_file.open(mode="w") as new_fp:
        with file.open(mode="r") as fp:
            for line in fp:
                data = from_tb_format(line)
                if data["model"] == TREE:
                    bush = create_bush(data)
                    new_fp.write(bush)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="The TB file you want to compare distances to", nargs=1)
    args = parser.parse_args()

    handle_file(Path(args.source))
