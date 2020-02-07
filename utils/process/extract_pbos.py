import sys
import os
import shutil
import subprocess
from typing import List
from pathlib import Path
from gooey import Gooey, GooeyParser

FOLDER = Path(__file__).parents[2]
if str(FOLDER) not in sys.path:
    sys.path.insert(0, str(FOLDER))

from utils.funcs import copytree


class ExtractPBOs:
    NAME = "Extract PBOs"
    DESCRIPTION = (
        "Extracts PBOs in given folder.\n"
        + "Allows keeping only .p3ds, which is mainly useful if you don't plan on using Buldozer"
        + "This is NOT a replacement of Arma3P and should only be used in rare circumstances"
    )

    @classmethod
    def parser(cls, parent=None):
        if parent is None:
            parser = GooeyParser(description=cls.DESCRIPTION)
        else:
            sub = parent.add_parser(cls.__name__)
            parser = sub.add_argument_group(cls.NAME, description=cls.DESCRIPTION, gooey_options={"show_border": True})

        parser.add_argument("source", help="Folder with PBOs to unpack", widget="DirChooser", type=Path)
        parser.add_argument("target", help="Where to unpack", widget="DirChooser", type=Path, default="P:\\")
        parser.add_argument(
            "-m", "--models", help="Copies only models and configs", action="store_true", required=False, default=False
        )
        parser.add_argument(
            "--purge",
            help="Remove current files in target directory for this PBO",
            action="store_true",
            required=False,
        )
        parser.add_argument(
            "--terrain",
            help="Extract only terrain files (Ignore missions, UI, etc)",
            action="store_true",
            required=False,
            default=True,
        )
        parser.add_argument(
            "-wl",
            "--whitelist",
            help="Special Iron Front mode that unpacks only _terrain PBOs",
            action="store_true",
            required=False,
        )

        return parser

    @classmethod
    def run(cls, args):
        if hasattr(args, "command") and args.command != cls.__name__:
            return

        extract = cls(args)
        extract.mod_unpack()
        extract.final()

    def mikero_installed(self):
        return True

    def __init__(self, args):
        self.args = args
        self.source: Path = args.source
        self.target: Path = args.target

        self.FNULL = open(os.devnull, "w")

    def mod_unpack(self):
        if not self.target.is_dir():
            raise NotADirectoryError(f"Target directory '{self.target}' is not a directory")

        if not self.source.is_dir():
            raise NotADirectoryError(f"Source directory '{self.source}' is not a directory")

        ignored_files = self.create_ignore_list(self.source, self.target)
        whitelist = self.create_whitelist(self.source)

        # Unpack all the PBOs and move their unpacked contents to P drive
        print("### UNPACKING ###")
        for file in self.source.glob("*.pbo"):
            filename = file.stem
            if whitelist and filename not in whitelist:
                print(f"Skipping {filename}")
                continue
            if filename in ignored_files:
                print(f"Skipping {filename}")
                continue
            retval = self.pbo_unpack(file, filename)

    def create_ignore_list(self, source: Path, target: Path) -> List[str]:
        ignored_files = []
        ignore_list = ["anims", "dubbing", "language", "missions", "ui_"]
        ignore_list_always = ["dubbing"]

        for file in source.glob("*.pbo"):
            filename = file.stem
            ignore_names = [ignore_list, ignore_list_always][int(self.args.terrain)]
            for i in ignore_names:
                if i in filename:
                    ignored_files.append(file)

            if self.args.purge:
                if filename not in ignored_files:
                    if (target / filename).exists():
                        print(f"Purging {filename}")
                        shutil.rmtree(target / filename)

        return ignored_files

    def create_whitelist(self, source: Path) -> List[str]:
        if not self.args.whitelist:
            return []
        to_whitelist = ["ww2_terrainsif_", "ww2_terrainsww2_", "ww2_terrainsi44_", "ww2_objects_"]
        whitelist = []

        for file in source.glob("*.pbo"):
            filename = file.stem
            for i in to_whitelist:
                if i in filename:
                    whitelist.append(file)
                    print(f"Found {file}")
        return whitelist

    def pbo_unpack(self, file: Path, filename: str):
        print(f"Unpacking {filename}")
        # subprocess.call(["extractPBO", "-S", "-P", file])
        subprocess.call(["extractPBO", "-S", "-P", str(file)], stdout=self.FNULL, stderr=subprocess.STDOUT)

        # When extractPBO it should move unpacked folder to P drive
        unpacked: Path = self.source / filename
        include = (".p3d", ".cpp") if self.args.models else ()
        if unpacked.is_dir():
            for f in unpacked.iterdir():
                if not f.is_dir():
                    continue

                target: Path = self.target / f.stem
                print(f"Copying {f} to {target}")
                copytree(f, target, include=include)

                shutil.rmtree(f)
        else:
            return 1

    def final(self):
        pass


if __name__ == "__main__":

    @Gooey
    def cli():
        parser = ExtractPBOs.parser()
        ExtractPBOs.run(parser.parse_args())

    cli()
