from pathlib import Path
from utils.library import TbLibrary, TbLibraryCollection, ModelEntry

import unittest

folder: Path = Path(__file__).parent / "testdata"

class TestLibrary(unittest.TestCase):
    def test_loading(self):
        library = TbLibrary.from_file(folder / "a3_plants_bush.tml")
        for entry in library:
            print(entry)

    def test_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            TbLibrary.from_file(folder / "invalid.tml")

    def test_model(self):
        library = TbLibrary.from_file(folder / "a3_plants_plant.tml")
        model: ModelEntry = list(library)[0]

        self.assertEqual(model.name, "bw_SetBig_Brains_F")
        self.assertFalse(model.landslope)


class TestLibraryCollection(unittest.TestCase):
    def test_collection(self):
        library = TbLibraryCollection(folder)
        entry: ModelEntry = library["bw_SetBig_Brains_F"]
        self.assertEqual(entry.name, "bw_SetBig_Brains_F")

        category = library.get_category('P_Reeds_F')
        self.assertEqual(category, "a3_plants_plant")

if __name__ == "__main__":
    unittest.main()
