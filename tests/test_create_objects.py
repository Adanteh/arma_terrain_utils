import unittest
import sys
import subprocess
from pathlib import Path

from utils.process.library import create_objects

file = Path(__file__)


class TestCreateObjects(unittest.TestCase):
    def test_create_objects(self):
        try:
            args = [
                sys.executable,
                create_objects.__file__,
                "--ignore-gooey",
                str(file.parent / "testdata"),
                "-o",
                str(file.parent / "testresults" / (file.stem + "_OUT.txt")),
                "-s",
                "20.0",
            ]
            output = subprocess.check_output(args)
        except subprocess.CalledProcessError as e:
            self.fail(e.output.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
