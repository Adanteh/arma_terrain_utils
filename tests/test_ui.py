import unittest
import sys
import subprocess
from utils import ui
from pathlib import Path

file = Path(__file__)


class TestGooeyUI(unittest.TestCase):
    def test_gooey_ui(self):
        try:
            # fmt: off
            args = [
                sys.executable,
                ui.__file__,
                "--ignore-gooey",
                "Generate",
                "-o", str(file.parent / "testresults" / "library")
            ]
            # fmt: on
            output = subprocess.check_output(args)
        except subprocess.CalledProcessError as e:
            print(e.output)
            self.fail(e.output.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
