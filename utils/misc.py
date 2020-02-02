from typing import Union
from collections import OrderedDict


def dict_keys_lower(iterable: Union[OrderedDict, dict, list]):
    """Renames all key in orderdeddict recursively to lowercase"""
    newdict = type(iterable)()
    if type(iterable) in (dict, OrderedDict):
        for key in iterable.keys():
            newdict[key.lower()] = iterable[key]
            if type(iterable[key]) in (dict, list, OrderedDict):
                newdict[key.lower()] = dict_keys_lower(iterable[key])
    elif type(iterable) is list:
        for item in iterable:
            item = dict_keys_lower(item)
            newdict.append(item)
    else:
        return iterable
    return newdict
