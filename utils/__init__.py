# from .ui import cli
# from .library.generate import main as generate
# from .library.create_objects import main as create

import colorama
import sys
from ansimarkup import AnsiMarkup, parse
 
if "--debug" in sys.argv:
    sys.argv.remove("--debug")
else: 
    sys.tracebacklimit = 0
    
colorama.init()
user_tags = {
    "error": parse("<K><r><b>"),
    "grey": parse(""),
}

am = AnsiMarkup(tags=user_tags)


def print(*args, **kwargs):
    """AnsiMarkup print wrapper with custom tags"""
    am.ansiprint(*args, **kwargs)
