import sys
from pathlib import Path

from gooey import Gooey, GooeyParser

FOLDER = Path(__file__).parents[1]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))


from utils.process.library.generate import Generate  # noqa: E402
from utils.process.library.create_objects import CreateObjects  # noqa: E402
from utils.process.tml_filter import TmlFilter  # noqa: E402
from utils.process.add_objects import AddExtraObject  # noqa: E402
from utils.process.filter_nearby import NearbyFiltering  # noqa: E402
from utils.process.random_offset import RandomOffset  # noqa: E402


@Gooey(advanced=True)
def cli():
    parser = GooeyParser(description="Arma terrain utils")
    parent = parser.add_subparsers(help="Utilities", dest="command")

    # TmlFilter.parser(parser=parser)
    Generate.parser(parent=parent)
    CreateObjects.parser(parent=parent)
    AddExtraObject.parser(parent=parent)
    NearbyFiltering.parser(parent=parent)
    RandomOffset.parser(parent=parent)

    args = parser.parse_args()

    # TmlFilter.run(args)
    Generate.run(args=args)
    CreateObjects.run(args=args)
    AddExtraObject.run(args=args)
    NearbyFiltering.run(args=args)
    RandomOffset.run(args=args)

    return parser


if __name__ == "__main__":
    cli()
