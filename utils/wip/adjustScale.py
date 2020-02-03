r"""
Used to split adjust scales for given object categories with an already existing TB export file
Open up CMD in Pythia folder and use:

python -m ObjectPlacement.utils.adjustScale
python -m ObjectPlacement.utils.adjustScale "ObjectPlacement\tests\TestProject\TerrainBuilder\testdata_tb.txt" -f "WW2 .Vegetation: Trees" -s 0.4
"""

import logging
import os
import subprocess
import sys
import pip
import argparse
import collections
import random
from shutil import copy2
from pathlib import Path

from ObjectPlacement.pyarma.terrains import tb_library
from ObjectPlacement.pyarma.common.colorsLog import print_error, print_green, print_magenta, print_blue, print_yellow, print_grey

def offset(current, offset, prevent_neg=False):
    return str(round(current + random.uniform(-offset/2, offset/2), 3))

def load_library(path=""):
    if path is "":
        path = Path(__file__).parent.parent.parent / "Exports" / "Library"
    else:
        path = Path(path)
        if not path.exists():
            print_error("Incorrect library folder path given: {}".format(path))
            raise NotADirectoryError
    return tb_library.tbLibraryCache(str(path), verbose=False)

def scale_adjust(args):
    """Reads data from slopeModels file"""

    filepath = args.tb_file[0]
    if not os.path.isfile(filepath):
        print_error("'{}' is not a valid path".format(filepath))
        raise FileNotFoundError

    with open(filepath, 'r') as write_file:
        objectlines = write_file.readlines()

    librarycache = load_library(args.library)
    linesedited = [adjust_entry(objectentry.strip(), args, librarycache) + "\n" for objectentry in objectlines]

    # Keep backup
    copy2(filepath, filepath + ".orig")
    with open(filepath, 'w') as write_file:
        write_file.writelines(linesedited)
    return 0

def adjust_entry(objectentry, args, librarycache=None):
    if librarycache is None:
        librarycache = load_library(args.library)

    tb_object = tb_library.TbObject.from_tb_format(objectentry)
    category = librarycache.get_model_category(tb_object.classname.lower())

    if not args.filter or category in args.filter:
        print_blue(tb_object.classname)
        scaleadjust = args.scale
        pitchadjust = args.pitch
        bankadjust = args.bank
        yawadjust = args.yaw

        if scaleadjust > 0:
            tb_object.scale = offset(tb_object.scale, scaleadjust)
        if pitchadjust > 0:
            tb_object.rotation[0] = offset(tb_object.rotation[0], pitchadjust)
        if bankadjust > 0:
            tb_object.rotation[1] = offset(tb_object.rotation[1], bankadjust)
        if yawadjust > 0:
            yaw = float(offset(tb_object.rotation[2], yawadjust))
            if yaw < 0:
                yaw = yaw + 360
            if yaw > 360:
                yaw = yaw - 360
            tb_object.rotation[2] = str(yaw)
    else:
        return objectentry

    return tb_object.tb_format()

PATH = Path(__file__).parent.parent
class AdjustScaleArgs(object):
    def __init__(
        self,
        tb_file=str(PATH / 'tests' / 'TestProject' / "TerrainBuilder" / 'testdata_tb.txt'),
        library_folder="",
        categories=[],
        scale=0,
        pitch=0,
        bank=0,
        yaw=0
    ):

        self.tb_file = [tb_file]
        self.library = library_folder
        self.scale = scale
        self.pitch = pitch
        self.bank = bank
        self.yaw = yaw
        self.filter = categories

if __name__ == '__main__':
    if len(sys.argv) == 1:
        from ObjectPlacement.utils.ui.adjustScale_ui import main as adjustscale_ui
        adjustscale_ui()
    else:
        parser = argparse.ArgumentParser(description='TML Generation Script')
        parser.add_argument('tb_file', help='.txt file that contains TB export', nargs=1)
        parser.add_argument('-l', '--library', help='Path to folder containing the library files', required=False, type=str, default="")
        parser.add_argument('-f', '--filter', help='Which library a file should be in to have its scale adjusted', required=False, nargs='+')
        parser.add_argument('-s', '--scale', help='Amount of scale to randomize', required=False, type=float, default=0)
        parser.add_argument('-p', '--pitch', help='Amount of pitch to randomize', required=False, type=float, default=0)
        parser.add_argument('-b', '--bank', help='Amount of bank to randomize', required=False, type=float, default=0)
        parser.add_argument('-y', '--yaw', help='Amount of yaw to randomize', required=False, type=float, default=0)
        args = parser.parse_args()
        scale_adjust(args)
