import itertools
from typing import Sequence, Iterable, Any, Optional
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

from ProjFormatter.utils.dict_utils import dicts_equal_ignore_keys
from ProjFormatter.utils.element_utils import get_child_count, are_relevant_elements, are_elements_equal, \
    copy_element


def _generate_subgroups_as_lists(lst: Sequence[Any]) -> list[tuple[Any, ...]]:
    """
    Generate all possible subsets of the input sequence that contain at least two elements.
    """
    subgroups = []
    for r in range(2, len(lst) + 1):
        subgroups.extend(itertools.combinations(lst, r))
    return subgroups


def _merge_conditions(elements_with_conditions: Iterable[ElementTree]):
    conditions = set([element.attrib["Condition"] for element in elements_with_conditions])
    conditions_strings = ["({})".format(condition) for condition in conditions]
    return " || ".join(conditions_strings)


def _merge_side_of_group(children_to_merge: Sequence[ElementTree], top: bool) -> Optional[ElementTree]:
    """
    Merge either top or bottom side of the group.
    :param top: If True, merge the top side of the group.
        If False, merge the bottom side of the group.
    :return: The merged element.
        None if no merge was done.
    """
    merged_element = Element(children_to_merge[0].tag, attrib=children_to_merge[0].attrib)
    merged_element.attrib["Condition"] = _merge_conditions(children_to_merge)

    if top:
        merge_index = 0
    else:
        merge_index = -1

    while True:
        # One of the elements has run out of grandchildren to merge
        if any(get_child_count(child_to_merge) == 0 for child_to_merge in children_to_merge):
            break

        merge_index_grandchildren = [child_to_merge[merge_index] for child_to_merge in children_to_merge]

        if not are_elements_equal(merge_index_grandchildren):
            # Found a unique grandchild, stop merging
            break

        # Move the common element to the merged result
        merged_element.append(copy_element(merge_index_grandchildren[0]))
        for child_to_merge in children_to_merge:
            child_to_merge.remove(child_to_merge[merge_index])

    if get_child_count(merged_element) > 0:
        return merged_element
    return None


def _should_merge_elements(element1: ElementTree, element2: ElementTree) -> bool:
    return element1.tag == element2.tag and not are_relevant_elements(element1, element2) and \
        dicts_equal_ignore_keys(element1.attrib, element2.attrib, ["Condition"])


def merge_conditional_elements(root: ElementTree):
    """
    What it does is find a group of subsequent elements that are all the same type but different conditions, meaning
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
    <A Condition="'$(Platform)'='Win32'">
        <B>b</B>
        <D>d</D>
        <F>f</F>
    </A>

    turns into

    <A Condition="'$(Platform)'='x64' || '$(Platform)'='Win32'">
        <B>b</B>
    </A>
    <A Condition="'$(Platform)'='x64'">
        <C>c</C>
    </A>
    <A Condition="'$(Platform)'='Win32'">
        <D>d</D>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Platform)'='Win32'">
        <F>f</F>
    </A>

    And this is done for each subgroup too, not just the largest group, so out of a group of 4 we could get conditions
    that are relevant only in 3 conditionals. Can that then break stuff.......? it can't if we update the contents.

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

    If no items were deleted, it could continue and then find the next subgroup which is x64Debug and Win32Debug and then do:

    <A Condition="'$(Platform)'='x64' || '$(Platform)'='Win32' || '$(Configuration)'='Release'">
        <C>c</C>
    </A>
    <A Condition="'$(Platform)'='x64' || '$(Platform)'='Win32' || '$(Configuration)'='Debug'">
        <B>b</B>
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

    And of course, if it knows that the only possible Platform values are x64 and Win32, it can remove that condition:

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

    To make this feature possible, we should get a dict called possible conditions which would hold a key condition word
    and a list of possible values. This should probably be the last part of this feature that I implement.
    Actually, it could even be a separate thing. We can call it optimize conditions where it checks if a condition
    covers all possible options, in which case the condition is just removed.
    That way, we also optimize cases where the user accidentally didn't optimize all conditions.
    If we do it in a separate function, this function will generate unoptimized conditions, which isn't ideal,
    but whatever, we will just call optimize conditions after this function.
    """
    current_children_to_merge = []

    for child_index in range(get_child_count(root)):
        merge_conditional_elements(root[child_index])

        if not current_children_to_merge or _should_merge_elements(current_children_to_merge[0], root[child_index].tag):
            current_children_to_merge.append(root[child_index])
        else:
            # Found an item that cannot be part of the current group, searching stage done, merge the current group
            if len(current_children_to_merge) > 1:
                for subgroup in _generate_subgroups_as_lists(current_children_to_merge):
                    top_merged_element = _merge_side_of_group(subgroup, True)
                    if top_merged_element:
                        root.insert(child_index, top_merged_element)

                    bottom_merged_element = _merge_side_of_group(subgroup, False)
                    if bottom_merged_element:
                        root.insert(child_index + len(current_children_to_merge), top_merged_element)

            current_children_to_merge = [root[child_index]]
