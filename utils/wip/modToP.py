#!/usr/bin/env python3
"""
This unapcks the given paths PBOs into P with the proper prefixes
Main reason to use this is if you only want to unpack terrain-related PBOs (using either the whitelist or -t mode)
Another reason is if you jusst want to be able to pack the terrain with pboProject and you need only the model and config files unpacked, saves a lot of disk space this way

Open up a CMD in the Pythia folder and do
    py -m ObjectPlacement.utils.modToP <path> -m

"""


import sys
import winreg

import os
import shutil
import subprocess
import glob
import argparse

from ObjectPlacement.pyarma.common.colorsLog import print_error, print_green, print_magenta, print_blue, print_yellow, print_grey, print_cyan
from ObjectPlacement.pyarma.common.copytree import copytree, copytree_extensionfilter

def install_tools():
    from .installMikero import install
    install()

class modToP(object):
    def __init__(self, targetpath):
        self.targetpath = targetpath
        self.FNULL = open(os.devnull, 'w')
        self.terrainmode = False
        self.purgemode = False
        self.modelsonly = False
        self.test = False

    def create_ignore_list(self, targetpath):
        ignored_files = []
        ignore_list = ['anims', 'dubbing', 'language', 'missions', 'ui_']
        ignore_list_always = ['dubbing']
        files = glob.glob("*.pbo")

        for file in files:
            filename = os.path.splitext(file)[0]
            ignore_names = [ignore_list, ignore_list_always][int(self.terrainmode)]
            for i in ignore_names:
                if i in filename:
                    ignored_files.append(file)
                    #print("Ignoring {}".format(file))
            if self.purgemode:
                if file not in ignored_files:
                    if os.path.isdir(os.path.join(targetpath, filename)):
                        print("Purging {}".format(filename))
                        shutil.rmtree(os.path.join(targetpath, filename))
        return ignored_files

    def create_whitelist(self, targetpath):
        white_list_found = []
        if not self.whitelist: return []
        white_list = ['ww2_terrainsif_', 'ww2_terrainsww2_', 'ww2_terrainsi44_', 'ww2_objects_']
        files = glob.glob("*.pbo")

        for file in files:
            filename = os.path.splitext(file)[0]
            for i in white_list:
                if i in filename:
                    white_list_found.append(file)
                    print_green("Found {}".format(file))
        return white_list_found


    def pbo_unpack(self, file, filename):
        print_green("Unpacking {}".format(file))
        # subprocess.call(["extractPBO", "-S", "-P", file])
        subprocess.call(["extractPBO", "-S", "-P", file], stdout=self.FNULL, stderr=subprocess.STDOUT)

        # When extractPBO it should move unpacked folder to P drive
        source = os.path.join(self.sourcepath, filename)
        if os.path.isdir(source):
            for folderunpack in os.listdir(source):
                targetpath = os.path.join(self.targetpath, folderunpack)
                print_cyan("Copying {} to {}".format(folderunpack, targetpath))
                if self.modelsonly:
                    copytree_extensionfilter(os.path.join(source, folderunpack), targetpath, ['.p3d', '.cpp'])
                else:
                    copytree(os.path.join(source, folderunpack), targetpath)

                shutil.rmtree(os.path.join(self.sourcepath, filename))
        else:
            return 1

    def mod_unpack(self, sourcepath):
        self.sourcepath = sourcepath
        os.chdir(self.sourcepath)

        ignored_files = self.create_ignore_list(self.targetpath)
        white_list = self.create_whitelist(self.targetpath)

        # Unpack all the PBOs and move their unpacked contents to P drive
        print('\n')
        pbos = glob.glob("*.pbo")
        if self.test:
            pbos = pbos[:5]
        print_magenta('### UNPACKING ###')
        for file in pbos:
            filename = os.path.splitext(file)[0]
            if self.whitelist:
                if file not in white_list:
                    print_yellow("Skipping {}".format(filename))
                    continue
            if file not in ignored_files:
                retval = self.pbo_unpack(file, filename)
            else:
                print_yellow("Skipping {}".format(filename))

def main(args):
    print_yellow("""
  ##################
  #     ModToP     #
  ##################
""")

    toolspath = os.path.dirname(os.path.realpath(__file__))
    if not (os.path.isdir(args.target)):
        print_error("Target {} does not exist, use Arma 3 Tools to Mount project drive".format(args.target))
        return 1

    unpacker = modToP(args.target)

    unpacker.purgemode = args.purge
    unpacker.terrainmode = args.terrain
    unpacker.whitelist = args.whitelist
    unpacker.modelsonly = args.models
    unpacker.test = args.test

    # Decrypt all the EBO files
    for sourcepath in args.path:
        if os.path.isdir(sourcepath):
            unpacker.mod_unpack(sourcepath)
        else:
            print_error('Invalid path: {}'.format(sourcepath))

    repl = input("Press ANY key to exit")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mod depbo script')
    parser.add_argument('-p', '--purge', help='Remove current files in target directory for this PBO', action="store_true", required=False, default=False)
    parser.add_argument('-t', '--terrain', help='Extract only terrain files (Ignore missions, UI, etc)', action="store_true", required=False, default=True)
    parser.add_argument('-wl', '--whitelist', help='Special Iron Front mode that unpacks only _terrain PBOs', action="store_true", required=False, default=False)
    parser.add_argument('-m', '--models', help='Copies only models and configs', action="store_true", required=False, default=False)
    parser.add_argument('--test', help='Test Mode, only does first 5 PBOs', action="store_true", required=False, default=False)
    parser.add_argument('--target', help='Target path to unpack. Default is P drive', required=False, default='P:\\')
    parser.add_argument('path', help='Path(s) to mod to extract', nargs='+')
    args = parser.parse_args()

    install_tools()
    sys.exit(main(args))
