from typing import List
from pathlib import Path
from collections import namedtuple


def clean_name(name: str) -> str:
    """Simplifies folder names, for better more logical grouping"""

    # Apex prefix instead of _exp suffix
    for prefix, suffix in (("apex", "_exp"), ("malden", "_argo"), ("enoch", "_enoch")):
        if name.find(suffix) != -1:
            name = name.replace(suffix, "")
            if name.startswith("a3"):
                name = name.replace("a3", prefix)
            else:
                name = prefix + name

    # A3
    for cleanup in (
        "_epa",
        "_epb",
        "_epc",
        "_beta",
        "_gamma",
        "_mark",
        "_bootcamp",
        "_heli",
        "_pmc",
        "_orange",
        "_jets",
    ):
        name = name.replace(cleanup, "")

    # Group up all CUP misc items
    if name.find("ca_misc") != -1:
        name = "ca_misc"

    name = name.replace("cup_terrains_cup_terrains", "cup")

    # Give takistan a better name
    if name.endswith("_e") or name.find("_e_"):
        name = name.replace("_e", "")
        name = name.replace("ca_", "taki_")

    if name.endswith("_e2") or name.find("_e2_"):
        name = name.replace("_e2", "")
        name = name.replace("ca_", "summer_")

    if name.find("buildings2") != -1 or name.find("_cti") != -1:
        nametemp = name.split("_")[:3]
        name = "_".join(nametemp)

    name = name.replace("vegetation", "veg")
    name = name.replace("structures", "struc")
    name = name.replace("civilian", "civ")
    name = name.replace("infrastructure", "infra")
    return name


def get_category_custom(relative_path: Path) -> namedtuple:
    """Returns named category, to autogroup objects and assign colors when creating a new library"""

    model_path = str(relative_path).lower()

    def func(path):
        return model_path.find(path) >= 0

    def is_category(types: List[str]):
        return bool(list(filter(func, types)))

    Category = namedtuple("Category", ["category", "fill", "outline"])
    if is_category(["tree", "treeparts"]):
        return Category(category="tree", fill=-16760832, outline=-1)

    if is_category(["vegetation", "bush", "plant", "clutter", "misc"]):
        return Category(category="bush", fill=-16727808, outline=-1)

    if is_category(["decal"]):
        return Category(category="roads", fill=-79905, outline=-16777216)

    if is_category(["signs"]):
        return Category(category="roads", fill=-15653149, outline=-16777216)

    if is_category(["road", "bridges"]):
        return Category(category="roads", fill=-12566464, outline=-1)

    if is_category(["rock"]):
        return Category(category="rocks", fill=-8553091, outline=-1)

    if is_category(["rail"]):
        return Category(category="rail", fill=-16711694, outline=-1)

    if is_category(["castle"]):
        return Category(category="castle", fill=-10912896, outline=-1)

    if is_category(["wall", "fence"]):
        return Category(category="walls", fill=-35827, outline=-16777216)

    if is_category(["wreck"]):
        return Category(category="wreck", fill=-8039340, outline=-1)

    if is_category(["\\ind"]):
        return Category(category="industry", fill=-8892372, outline=-1)

    if is_category(["\\mil"]):
        return Category(category="industry", fill=-7960491, outline=-1)

    if is_category(["structures", "buildings"]):
        return Category(category="structures", fill=-9673539, outline=-16777216)

    return Category(category="", fill=-16777216, outline=-1)
