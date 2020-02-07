"""
    Adds a bush near every tree
"""
import sys
from pathlib import Path
from random import uniform
from math import cos, sin
from gooey import Gooey, GooeyParser

FOLDER = Path(__file__).parents[2]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))


from utils.tb import TbRow  # noqa: E402


class AddExtraObject:
    NAME = "Add Extra Objects"
    DESCRIPTION = (
        "Tool to add extra objects near every entry of given object, can be used to place\n"
        + "bushes near trees for example"
    )

    @classmethod
    def parser(cls, parent=None):
        if parent is None:
            parser = GooeyParser(description=cls.DESCRIPTION)
        else:
            sub = parent.add_parser(cls.__name__)
            parser = sub.add_argument_group(cls.NAME, description=cls.DESCRIPTION, gooey_options={"show_border": True})

        parser.add_argument("--input", help="File to process", widget="FileChooser", type=Path, required=True)
        parser.add_argument("--target", help="Model to add extra objects near", required=True, default="t_Inocarpus_F")
        parser.add_argument("--model", help="Which model to place", required=True, default="b_Leucaena_F")
        parser.add_argument("--amount", help="How many objects to place near each entry", default=2, type=int)
        parser.add_argument("--radius", help="Maximum distance to place object at", default=2.0, type=float)
        return parser

    @classmethod
    def run(cls, args):
        if hasattr(args, "command") and args.command != cls.__name__:
            return

        file_in = args.input
        file_out = args.input.parent / args.input.stem + "_out.txt"
        target_model = args.target.lower()

        with file_out.open(mode="w") as new_fp:
            with file_in.open(mode="r") as fp:
                for line in fp:
                    entry = TbRow(line)
                    if entry.model.lower() == target_model:
                        for i in range(0, args.amount):
                            bush = create_new_object(entry, args.model, args.radius)
                            new_fp.write(bush)


def create_new_object(entry: TbRow, model: str, radius: float):
    angle = round(uniform(0, 360), 3)
    new_object = TbRow(
        model=model,
        x=entry.x + radius * cos(angle),
        y=entry.y + radius * sin(angle),
        dir=round(uniform(0, 360), 3),
        pitch=0.0,
        bank=0.0,
        scale=round(uniform(2, 0.5), 3),
        z=0.0,
    )
    return new_object.as_line() + "\n"


if __name__ == "__main__":

    @Gooey
    def cli():
        parser = AddExtraObject.parser()
        AddExtraObject.run(parser.parse_args())

    cli()
