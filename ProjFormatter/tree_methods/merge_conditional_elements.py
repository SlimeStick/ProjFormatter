import itertools
from typing import Any
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

from ProjFormatter.utils.dict_utils import dicts_equal_ignore_keys
from ProjFormatter.utils.element_utils import get_children, get_child_count, are_relevant_elements, are_elements_equal, \
    copy_element


def _generate_subgroups_as_lists(lst: list[Any]) -> list[tuple[Any, ...]]:
    """
    Generate all possible subsets of the input list that contain at least two elements.
    """
    subgroups = []
    for r in range(2, len(lst) + 1):
        subgroups.extend(itertools.combinations(lst, r))
    return subgroups


def _merge_conditions(elements_with_conditions: list[ElementTree]):
    conditions = set([element.attrib["Condition"] for element in elements_with_conditions])
    conditions_strings = ["({})".format(condition) for condition in conditions]
    return " || ".join(conditions_strings)


def _merge_top_group(children_to_merge: list[ElementTree]) -> ElementTree:
    merged_element = Element(children_to_merge[0].tag, attrib=_merge_conditions(children_to_merge))

    grandchild_index = 0

    while True:
        # One of the elements has run out of grandchildren to merge
        if any(get_child_count(child_to_merge) <= grandchild_index for child_to_merge in children_to_merge):
            break

        ith_grandchildren = [child_to_merge[grandchild_index] for child_to_merge in children_to_merge]

        if are_elements_equal(ith_grandchildren):
            # Move the common element to the merged result
            merged_element.append(copy_element(ith_grandchildren[0]))

            for child_to_merge in children_to_merge:
                del child_to_merge[grandchild_index]
                # grandchild_index is not incremented as the next element shifts into position
        else:
            # Found a mismatch, abort merge
            break

    if get_child_count(merged_element) > 0:
        return merged_element
    return None


def _should_merge_elements(element1: ElementTree, element2: ElementTree) -> bool:
    return element1.tag == element2.tag and not are_relevant_elements(element1, element2) and \
        dicts_equal_ignore_keys(element1.attrib, element2.attrib, ["Condition"])


def merge_conditional_elements(root):
    """
    What it does is find a group of subsequent elements that are all of the same type but different conditions, meaning
    that no two elements in the group can exist at the same time.
    Then from that group, it creates a new element which goes before all of them, which has a single condition of all of them,
    that has the contents of all the elements' contents up until an element has different content.
    Then it also creates an element like that but from the bottom that merges elements from the bottom.

    So we get something like this:
    <A Condition="'$(Platform)'='x64'">
        <B>b</B>
        <C>c</C>
        <F>f</F>
    </A>
    <A Condition="'$(Platform)'='x65'">
        <B>b</B>
        <D>d</D>
        <F>f</F>
    </A>

    turns into

    <A Condition="'$(Platform)'='x64' || '$(Platform)'='x65'">
        <B>b</B>
    </A>
    <A Condition="'$(Platform)'='x64'">
        <C>c</C>
    </A>
    <A Condition="'$(Platform)'='x65'">
        <D>d</D>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Platform)'='x65'">
        <F>f</F>
    </A>

    And this is done for each subgroup too, not just the largest group, so out of a group of 4 we could get conditions
    that are relevant only in 3 conditionals. Can that then break stuff? errmmm.......

    So like let's say I have this case:
    <A Condition="'$(Platform)'='x64' || '$(Configuration)'='Debug'">
        <B>b</B>
        <D>d</D>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Configuration)'='Release'">
        <C>c</C>
        <E>e</E>
    </A>
    <A Condition="'$(Platform)'='Win32' || '$(Configuration)'='Debug'">
        <B>b</B>
        <F>f</F>
    </A>
    <A Condition="'$(Platform)'='Win32' || '$(Configuration)'='Release'">
        <C>c</C>
        <G>g</G>
    </A>

    It would see it cannot merge anything in the large group.
    Then it would try every subgroup until it got x64Release and Win32Release which it would then merge to create:
    <A Condition="'$(Platform)'='x64' || '$(Platform)'='Win32' || '$(Configuration)'='Release'">
        <C>c</C>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Configuration)'='Debug'">
        <B>b</B>
        <D>d</D>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Configuration)'='Release'">
        <E>e</E>
    </A>
    <A Condition="'$(Platform)'='Win32' || '$(Configuration)'='Debug'">
        <B>b</B>
        <F>f</F>
    </A>
    <A Condition="'$(Platform)'='Win32' || '$(Configuration)'='Release'">
        <G>g</G>
    </A>

    After every merge does it need to start the loop again because the items have changed? or can it just continue from
    where it was?
    I think it must start again only if the merge deleted items, because then the subgroups are invalidated.

    If no items were deleted it could continue and then find the next subgroup which is x64Debug and Win32Debug and then do:

    <A Condition="'$(Platform)'='x64' || '$(Platform)'='Win32' || '$(Configuration)'='Release'">
        <C>c</C>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Platform)'='Win32' || '$(Configuration)'='Debug'">
        <C>c</C>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Configuration)'='Debug'">
        <D>d</D>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Configuration)'='Release'">
        <E>e</E>
    </A>
    <A Condition="'$(Platform)'='Win32' || '$(Configuration)'='Debug'">
        <F>f</F>
    </A>
    <A Condition="'$(Platform)'='Win32' || '$(Configuration)'='Release'">
        <G>g</G>
    </A>

    And of course if it knows that the only possible Platform values are x64 and Win32 it can remove that condition:

    <A Condition="''$(Configuration)'='Release'">
        <C>c</C>
    </A>
    <A Condition="'$(Configuration)'='Debug'">
        <C>c</C>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Configuration)'='Debug'">
        <D>d</D>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Configuration)'='Release'">
        <E>e</E>
    </A>
    <A Condition="'$(Platform)'='Win32' || '$(Configuration)'='Debug'">
        <F>f</F>
    </A>
    <A Condition="'$(Platform)'='Win32' || '$(Configuration)'='Release'">
        <G>g</G>
    </A>

    To make this feature possible we should get a dict called possible conditions which would hold a key condition word
    and a list of possible values. This should probably be the last part of this feature that I implement.
    Actually, it could even be a separate thing. We can call it optimize conditions where it checks if a condition
    covers all possible options, in which case the condition is just removed.
    That way we also optimize cases where the user accidentally didn't optimize all conditions.
    If we do it in a separate function, this function will generate unoptimized conditions, which isn't ideal,
    but whatever, we will just call optimize conditions after this function.
    """
    current_children_to_merge = None

    for child in get_children(root):
        merge_conditional_elements(child)

        # Found first item of the current group
        if not current_children_to_merge:
            current_children_to_merge = [child]
            continue

        # Found another item for the current group
        if _should_merge_elements(current_children_to_merge[0], child.tag):
            current_children_to_merge.append(child)
        else:
            # Found an item that cannot be part of the current group, searching stage done, merge the current group
            if get_child_count(current_children_to_merge) != 1:
                for subgroup in _generate_subgroups_as_lists(current_children_to_merge):
                    top_merged_element = _merge_top_of_group(subgroup)
                    # None if there was nothing aggregate at the top
                    if top_merged_element:
                        # Add to top of tree somehow
                        pass

                    bottom_merged_element = _merge_bottom_of_group(subgroup)
                    # None if there was nothing aggregate at the bottom
                    if bottom_merged_element:
                        # Add to bottom of tree somehow
                        pass

            current_children_to_merge = [child]
