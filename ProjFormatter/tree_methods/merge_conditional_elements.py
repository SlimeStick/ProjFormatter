import itertools
from typing import Any

from ProjFormatter.utils.element_utils import get_children, get_child_count


def _generate_subgroups_as_lists(lst: list[Any]) -> list[tuple[Any, ...]]:
    """
    Generate all possible subsets of the input list that contain at least two elements.
    """
    subgroups = []
    for r in range(2, len(lst) + 1):
        subgroups.extend(itertools.combinations(lst, r))
    return subgroups


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
    current_children_to_merge = []

    for child in get_children(root):
        merge_conditional_elements(child)

        if not current_children_to_merge:
            current_children_to_merge.append(child)
            continue

        # TODO: Check if current_children_to_merge[0].attrib is a known configuration and if it is then allow it
        if child.tag != current_children_to_merge[0].tag and child.attrib != current_children_to_merge[0].attrib:
            if get_child_count(current_children_to_merge) == 1:
                current_children_to_merge = [child]
                continue

            # Returned here because we need to append it before all the items we just merged
            merged_element = _merge_elements_of_same_tag(root, current_children_to_merge)
