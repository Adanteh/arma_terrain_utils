import unittest
from pathlib import Path

from utils.library import ModelEntry, TbLibrary, TbLibraryCollection
from datetime import datetime

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

        self.assertEqual(model.name, "p_Reeds_F")
        self.assertFalse(model.landslope)

    def test_dict_insensitive(self):
        library = TbLibrary.from_file(folder / "a3_plants_plant.tml")
        self.assertEqual(library["p_reeds_f"]["Name"], "p_Reeds_F")

    def test_save(self):
        library = TbLibrary.from_file(folder / "a3_plants_plant.tml")
        library["p_reeds_f"]["Date"] = str(datetime.now())
        library.save(path=(folder.parent / "testresults" / "a3_plants_plants.tml"))

class TestLibraryCollection(unittest.TestCase):
    def test_collection(self):
        library = TbLibraryCollection(folder)
        entry: ModelEntry = library["bw_SetBig_Brains_F"]
        self.assertEqual(entry.name, "bw_SetBig_Brains_F")

        category = library.get_category("P_Reeds_F")
        self.assertEqual(category, "a3_plants_plant")

        entry: ModelEntry = library.get_entry("P_Reeds_F")
        self.assertEqual(entry.size, (4.7428550000000005, 3.439329, 4.717775))


if __name__ == "__main__":
    unittest.main()
