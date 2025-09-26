from typing import Sequence, Iterable, Optional
from xml.etree.ElementTree import Element

from defusedxml import ElementTree
from ordered_set import OrderedSet

from ProjFormatter.trees.xml_tree import XMLTree
from ProjFormatter.utils.dict_utils import dicts_equal_ignore_keys
from ProjFormatter.utils.element_utils import get_child_count, are_elements_equal, copy_element
from ProjFormatter.utils.math_utils import generate_subgroups_as_lists


class MSBuildTree(XMLTree):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.check_format_sanity()

    def check_format_sanity(self):
        self.check_root_node()

    def check_root_node(self):
        """
        Checks that the root element is valid.
        """
        if self.root.tag != "Project":
            raise ValueError("The root node must be a Project element")
        if self.namespace != "http://schemas.microsoft.com/developer/msbuild/2003":
            raise ValueError("The namespace must be 'http://schemas.microsoft.com/developer/msbuild/2003'")

    def remove_labels(self):
        """
        Removes all Labels as any Label attributes are arbitrary tags that are only used by Visual Studio as signposts
        for editing; they have no other function.
        """
        self.remove_attributes(["Label"])

    def format_conditions(self):
        """
        Strips conditions so that it's easier to see when conditions are equal.
        """
        for element in self.root.iter():
            if "Condition" in element.attrib:
                element.attrib["Condition"] = element.attrib["Condition"].strip()

    @classmethod
    def _merge_conditions(cls, elements_with_conditions: Iterable[ElementTree]):
        conditions = OrderedSet([element.attrib["Condition"] for element in elements_with_conditions])
        conditions_strings = ["({})".format(condition) for condition in conditions]
        return " Or ".join(conditions_strings)

    @classmethod
    def _merge_side_of_group(cls, children_to_merge: Sequence[ElementTree], top: bool) -> Optional[ElementTree]:
        """
        Merge either top or bottom side of the group.
        :param top: If True, merge the top side of the group.
            If False, merge the bottom side of the group.
        :return: The merged element.
            None if no merge was done.
        """
        merged_element = Element(children_to_merge[0].tag, attrib=children_to_merge[0].attrib)
        merged_element.attrib["Condition"] = cls._merge_conditions(children_to_merge)

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

    @classmethod
    def _should_merge_elements(cls, element1: ElementTree, element2: ElementTree) -> bool:
        return element1.tag == element2.tag and \
            dicts_equal_ignore_keys(element1.attrib, element2.attrib, ["Condition"])

    @classmethod
    def _merge_children(cls, root: ElementTree, current_children_to_merge: list[Element], child_index: int):
        if len(current_children_to_merge) > 1:
            for subgroup in generate_subgroups_as_lists(current_children_to_merge):
                top_merged_element = cls._merge_side_of_group(subgroup, True)
                if top_merged_element:
                    root.insert(child_index - len(current_children_to_merge), top_merged_element)
                    child_index += 1

                bottom_merged_element = cls._merge_side_of_group(subgroup, False)
                if bottom_merged_element:
                    root.insert(child_index, bottom_merged_element)

    @classmethod
    def _merge_conditional_elements(cls, root: ElementTree):
        current_children_to_merge = []

        child_index = 0
        while child_index < get_child_count(root):
            cls._merge_conditional_elements(root[child_index])

            if not current_children_to_merge or cls._should_merge_elements(current_children_to_merge[0],
                                                                           root[child_index]):
                current_children_to_merge.append(root[child_index])
            else:
                # Found an item that cannot be part of the current group, searching stage done, merge the current group
                cls._merge_children(root, current_children_to_merge, child_index)

                current_children_to_merge = [root[child_index]]
            child_index += 1
        cls._merge_children(root, current_children_to_merge, child_index)

    def merge_conditional_elements(self):
        """
        Merges groups of subsequent elements that are the type but have mutually exclusive conditions.
        Creates a merged element before and after each merge group.
        """
        self._merge_conditional_elements(self.root)
    def format_once(self):
        super().format_once()
        self.remove_labels()
        self.format_conditions()
        # TODO: Improve removal so that it doesn't recursively remove all elements but removes them using a context
        #   So for example it won't remove all ImportGroup elements because that may mean something else in a special
        #   context of a tag we don't know about. Instead remove only ImportGroups that appear inside a Project tag.
        self.remove_empty_elements(["PropertyGroup", "ImportGroup", "ItemDefinitionGroup", "ClCompile", "Link",
                                    "ItemGroup"])
        self.merge_elements_of_same_type()
        self.merge_conditional_elements()
