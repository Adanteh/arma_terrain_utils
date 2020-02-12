import unittest
from pathlib import Path
from typing import List

from utils.tb import tb_iterator, TbRow

folder: Path = Path(__file__).parent / "testdata"

class TestTB(unittest.TestCase):
    def test_iterator(self):
        entries: List[TbRow] = list(tb_iterator(folder / "test_tb_file.txt"))
        self.assertEqual(entries[0].model, "bw_SetBig_Brains_F")
        self.assertEqual(entries[-1].model, "p_Reeds_F")

    # def test_iterator_invalid(self):
    #     with self.assertRaises(FileNotFoundError):
    #         tb_iterator(folder / "test_INVALID.txt")

if __name__ == "__main__":
    unittest.main()
