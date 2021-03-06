# arma_terrain_utils
Assortment of Python scripts to be used for Arma or DayZ terrain making

## Usage
Requires Python 3.7+
Install requirements with pip

`pip install -r requirements.txt`

Run like `python utils\ui.py` or `python -m utils.ui`
Most scripts can also be run on their own by just executing them directly 

![Offset screenshot](readme/offset.png)

# Available scripts
## Generate
Creates a library for usage in Terrain Builder. Automatically categorizes based on names of subfolders,
assign colors, fixes duplicates and will ignore things like proxy objects (Which you shouldn't use)

## CreateObjects
Creates a .txt file containing an object for every single entry in given library folder
You usually want to do this after generating library, then import the entire Library into TB and then import the created file
It's mostly to give you a library that has info like SlopeContact, bounding box and so (Used by QGIS plugin and Plopper)

## AddExtraObject
Specific tool to add object of given type `model` in a `radius` around each entry of `target`
Can be useful if you want to add specific bush near a tree or something like that. 

## NearbyFiltering
Allows you to delete all objects that are closer than `radius` from another file
Useful if you have separate files for primary forest and undergrowth, and want to prevent clipping

## RandomOffset
Goes over each line in a file, and adds either coordinate offset to the position,
or randomizes values a bit. Useful to some pitch/bank randomness to files generated with Terrain Processor