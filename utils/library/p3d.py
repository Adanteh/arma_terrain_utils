"""
    Gets various info from a .p3d file, like slopeLandContact or bounding boxes
"""

import subprocess
from pathlib import Path


def slopelandcontact(path: Path) -> bool:
    """
        Checks if given p3d has slopeLandContact property, objects with this property should never
        have their pitch/bank adjusted when exporting for TB
    
    Args:
        path (Path): path to p3d 
    
    Returns:
        bool: True if slopeLandContact property is fo und
    """

    result = subprocess.check_output(["dep3d", "-LPP", str(path)])
    if result.lower().find("placement=slopelandcontact") != -1:
        return True
    return False

def boundingbox(path: Path) -> bool:
    """
        Checks if given p3d has slopeLandContact property, objects with this property should never
        have their pitch/bank adjusted when exporting for TB
    
    Args:
        path (Path): path to p3d 
    
    Returns:
        bool: True if slopeLandContact property is fo und
    """

    result = subprocess.check_output(["dep3d", "-LD", str(path)])
    bb_min = result.lower().find("box min")
    bb_max = result.lower().find("box max")
