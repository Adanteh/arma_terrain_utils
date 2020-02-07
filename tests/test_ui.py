import unittest
import sys
from utils.ui import cli, FOLDER
from utils.process.library.generate import Generate
from pathlib import Path

class TestUI(unittest.TestCase):
    def test_ui(self):
        sys.argv = [
            str(FOLDER / "utils" / "ui.py"),
            "--ignore-gooey",
            # Generate.NAME
        ]
        self.assertIsNotNone(cli())


if __name__ == "__main__":
    unittest.main()
