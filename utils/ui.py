import sys
from pathlib import Path

FOLDER = Path(__file__).parents[1]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

from gooey import Gooey, GooeyParser  # noqa: E402
from utils.library.generate import Generate  # noqa: E402
from utils.library.create_objects import CreateObjects  # noqa: E402


@Gooey(optional_cols=2, program_name="Arma terrain utilities", advanced=True)
def cli():
    parser = GooeyParser(description="Arma terrain utils")
    subs = parser.add_subparsers(help="Commands", dest="command")

    Generate.parser(subs)
    CreateObjects.parser(subs)
    args = parser.parse_args()
    Generate.run(args)
    CreateObjects.run(args)


if __name__ == "__main__":
    cli()
