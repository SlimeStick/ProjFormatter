import itertools
from typing import Any

from ProjFormatter.utils.element_utils import get_children, get_child_count, are_elements_equal
from defusedxml import ElementTree


def _generate_subgroups_as_lists(lst: list[Any]) -> list[tuple[Any, ...]]:
    """
    Generate all possible subsets of the input list that contain at least two elements.
    """
    subgroups = []
    for r in range(2, len(lst) + 1):
        subgroups.extend(itertools.combinations(lst, r))
    return subgroups


def _merge_elements_of_same_tag(root, children_to_merge):
    merged_element = ElementTree(children_to_merge[0].tag, attrib=children_to_merge[0].attrib)

    grandchild_index = 0
    while True:
        # One of the elements has ran out of grandchildren to merge
        if any(get_child_count(child_to_merge) <= grandchild_index for child_to_merge in children_to_merge):
            break

        ith_grandchildren = [child_to_merge[grandchild_index] for child_to_merge in children_to_merge]

        if are_elements_equal(ith_grandchildren):
            # Move the common element to the merged result
            first = ith_grandchildren[0]
            new_grandchild = ElementTree(first.tag, attrib=first.attrib)
            new_grandchild.text = first.text
            merged_element.append(new_grandchild)

            for child_to_merge in children_to_merge:
                del child_to_merge[grandchild_index]
                # grandchild_index is not incremented as the next element shifts into position
        else:
            # Found a mismatch, abort merge
            break

    return merged_element


def merge_elements_of_different_types(root):
    # The flow is to go over all children and for each:
    #
    # Insert the element in the current index
    # Start a subgroup and keep adding children to it as long as they have different conditions of the same format
    # When you encounter a relevant child, move grandchildren from the current subgroup into the new element

    for child in get_children(root):
        merge_elements_of_different_types(child)

    current_children_to_merge = []

    for child in get_children(root):
        if not current_children_to_merge:
            current_children_to_merge.append(child)
            continue

        if

        # TODO: Check if attrib is a known configuration and if it is then allow it
        if child.tag != current_children_to_merge[0].tag and child.attrib != current_children_to_merge[0].attrib:
            if get_child_count(current_children_to_merge) == 1:
                current_children_to_merge = [child]
                continue

            # Returned here because we need to append it before all the items we just merged
            merged_element = _merge_elements_of_same_tag(root, current_children_to_merge)
