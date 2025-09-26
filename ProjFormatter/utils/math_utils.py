import itertools
from typing import Sequence, Any


def generate_subgroups_as_lists(lst: Sequence[Any]) -> list[tuple[Any, ...]]:
    """
    Generate all possible subsets of the input sequence that contain at least two elements.
    """
    subgroups = []
    for r in range(2, len(lst) + 1):
        subgroups.extend(itertools.combinations(lst, r))
    return subgroups
