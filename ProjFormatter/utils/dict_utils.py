from typing import Any, Dict


def dicts_equal_ignore_key(dict1: Dict[Any, Any], dict2: Dict[Any, Any], key_to_ignore: Any) -> bool:
    for key, value in dict1.items():
        if key == key_to_ignore:
            continue
        if key not in dict2 or dict2[key] != value:
            return False
    for key in dict2:
        if key == key_to_ignore:
            continue
        if key not in dict1:
            return False
    return True
