import unittest
import sys
import subprocess
from pathlib import Path

from utils.process import random_offset

file = Path(__file__)


class TestRandomOffset(unittest.TestCase):
    def test_random_offset(self):
        try:
            # fmt: off
            args = [
                sys.executable,
                random_offset.__file__,
                "--ignore-gooey",
                str(file.parent / "testdata" / "test_tb_file.txt"),
                "-dir", "10",
                "-p", "1.0",
                "-zr", "1",
                "-s", "0.2",
                "-x", "1000",
                "-y", "10", 
                "-z", "2",
            ]
            # fmt: on
            output = subprocess.check_output(args)
        except subprocess.CalledProcessError as e:
            print(e.output)
            self.fail(e.output.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
