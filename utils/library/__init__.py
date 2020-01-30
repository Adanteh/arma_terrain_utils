from pathlib import Path


import colorama
from ansimarkup import AnsiMarkup, parse

ROOT_FOLDER = Path(__file__).parents[1]

colorama.init()
user_tags = {
    # Add a new tag (e.g. we want <info> to expand to "<bold><green>").
    "error": parse("<K><r><b>"),
    "grey": parse(""),
}

am = AnsiMarkup(tags=user_tags)


def print(*args, **kwargs):
    """AnsiMarkup print wrapper with custom tags"""
    am.ansiprint(*args, **kwargs)


if __name__ == "__main__":
    pass
