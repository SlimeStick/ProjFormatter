from typing import Any, Dict, Iterable


def dicts_equal_ignore_keys(dict1: Dict[Any, Any], dict2: Dict[Any, Any], keys_to_ignore: Iterable[Any]) -> bool:
    """
    Returns whether two dictionaries are equal, not including the keys to ignore.
    """
    for key, value in dict1.items():
        if key in keys_to_ignore:
            continue
        if key not in dict2 or dict2[key] != value:
            return False
    for key in dict2:
        if key in keys_to_ignore:
            continue
        if key not in dict1:
            return False
    return True
