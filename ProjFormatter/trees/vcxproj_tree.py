from typing import Sequence, Iterable, Optional
from xml.etree.ElementTree import Element

from defusedxml import ElementTree

from ProjFormatter.tree_traversers.level_order_traversal import LevelOrderTraverser
from ProjFormatter.trees.xml_tree import XMLTree
from ProjFormatter.utils.dict_utils import dicts_equal_ignore_keys
from ProjFormatter.utils.element_utils import get_child_count, are_relevant_elements, are_elements_equal, \
    copy_element
from ProjFormatter.utils.element_utils import get_children
from ProjFormatter.utils.math_utils import generate_subgroups_as_lists


class VCXProjTree(XMLTree):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.check_format_sanity()

    def check_include_sanity(self):
        """
        Checks that the Include attributes in all elements don't contain macro usages.
        """
        for element in self.root.iter():
            if "$" in element.attrib.get("Include", ""):
                raise ValueError("The Visual Studio C++ project system currently doesn't support macros in project item"
                                 " paths.")

    def check_project_configuration_elements(self):
        """
        Checks that the ProjectConfiguration elements inside the Project's ItemGroups are valid.
        """
        for child in get_children(self.root):
            if child.tag != "ItemGroup":
                continue
            for grandchild in get_children(child):
                if grandchild.tag != 'ProjectConfiguration':
                    continue
                if "Include" not in grandchild.attrib:
                    raise ValueError("ProjectConfiguration must have an Include attribute")
                grandchild_tags = [grandchild.tag for grandchild in get_children(grandchild)]
                if len(grandchild_tags) != 2:
                    raise ValueError("ProjectConfiguration must have 2 children")
                if not "Platform" in grandchild_tags:
                    raise ValueError("ProjectConfiguration must a Platform child")
                if not "Configuration" in grandchild_tags:
                    raise ValueError("ProjectConfiguration must a Configuration child")

    def get_project_configurations(self) -> list[str]:
        project_configurations = []
        for element in LevelOrderTraverser(self.root, 2):
            if element.tag == 'ProjectConfiguration':
                project_configurations.append(element.attrib["Include"])
        return project_configurations

    def check_project_configuration_combinations(self):
        """
        Checks that every combination of every configuration and platform defined in the vcxproj appears as a project
        configuration.
        """
        project_configurations = self.get_project_configurations()
        configurations = set()
        platforms = set()

        for project_configuration in project_configurations:
            configuration, platform = project_configuration.split("|")
            configurations.add(configuration)
            platforms.add(platform)

        for configuration in configurations:
            for platform in platforms:
                if f"{configuration}|{platform}" not in project_configurations:
                    raise ValueError("The IDE expects to find a project configuration for any combination of "
                                     "Configuration and Platform values used in all ProjectConfiguration items. ")

    def check_root_node(self):
        """
        Checks that the root element is valid.
        """
        if self.root.tag != "Project":
            raise ValueError("The root node must be a Project element")
        if self.namespace != "http://schemas.microsoft.com/developer/msbuild/2003":
            raise ValueError("The namespace must be 'http://schemas.microsoft.com/developer/msbuild/2003'")
        if "DefaultTargets" not in self.root.attrib:
            raise ValueError("The DefaultTargets attribute must be defined")

    def check_import_elements(self):
        """
        Makes sure that all Import elements are valid.
        """
        for element in self.root.iter():
            if element.tag != "Import":
                continue
            if "Project" not in element.attrib:
                raise ValueError("An Import element must have a Project attribute")

    def check_microsoft_cpp_default_props(self):
        """
        Makes sure that Microsoft.Cpp.default.props is imported.
        """
        for child in get_children(self.root):
            if child.tag != 'Import':
                continue
            if child.attrib["Project"] == r"$(VCTargetsPath)\Microsoft.Cpp.Default.props":
                return
        raise ValueError("Microsoft.Cpp.Default.props wasn't imported")

    def check_microsoft_cpp_props(self):
        """
        Makes sure that Microsoft.Cpp.props is imported.
        """
        for child in get_children(self.root):
            if child.tag != 'Import':
                continue
            if child.attrib["Project"] == r"$(VCTargetsPath)\Microsoft.Cpp.props":
                return
        raise ValueError("Microsoft.Cpp.props wasn't imported")

    def check_project_references(self):
        """
        Validates that the ProjectReferences elements are valid.
        """
        for child in get_children(self.root):
            if child.tag != "ItemGroup":
                continue
            for grandchild in get_children(child):
                if grandchild.tag != "ProjectReference":
                    continue
                if "Include" not in grandchild.attrib:
                    raise ValueError("ProjectReference must have an Include attribute")
                if "Condition" in grandchild.attrib:
                    raise ValueError("ProjectReference don't support conditions")
                for great_grandchild in get_children(grandchild):
                    if "Condition" in great_grandchild.attrib:
                        raise ValueError("ProjectReference metadata don't support conditions")

    def check_format_sanity(self):
        """
        Makes sure that the tree is in the vcxproj format.
        Should be called after editing the tree as according to Microsoft's documentation, manual editing mistakes can
        cause the IDE to crash or behave in unexpected ways.
        Implemented so that format testing can be done without running MSBuild to check for mistakes and because even
        MSBuild doesn't enforce all rules specified by Microsoft.
        """
        # TODO: Understand how many projects have $ in include statements
        # self.check_include_sanity()
        self.check_project_configuration_elements()
        self.check_project_configuration_combinations()
        self.check_root_node()
        self.check_import_elements()
        self.check_microsoft_cpp_default_props()
        self.check_microsoft_cpp_props()
        self.check_project_references()

        # TODO: More stuff we could check:
        #   . That ~stuff~ isn't used before Microsoft.Cpp.default.props is imported
        #   . That ~stuff~ isn't used before Microsoft.Cpp.props is imported
        #   . That UserMacros don't change between configurations
        #   . Understand how TF Per-configuration PropertyGroup elements work
        #   . Understand how TF Per-configuration ItemDefinitionGroup elements work
        #   . Make sure that ItemGroup elements don't have conditions on them
        #   . Maybe make sure that settings in ItemGroup elements are replicated for each configuration? WTF?

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
        conditions = set([element.attrib["Condition"] for element in elements_with_conditions])
        conditions_strings = ["({})".format(condition) for condition in conditions]
        return " || ".join(conditions_strings)

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
        return element1.tag == element2.tag and not are_relevant_elements(element1, element2) and \
            dicts_equal_ignore_keys(element1.attrib, element2.attrib, ["Condition"])

    @classmethod
    def _merge_conditional_elements(cls, root: ElementTree):
        current_children_to_merge = []

        for child_index in range(get_child_count(root)):
            cls._merge_conditional_elements(root[child_index])

            if not current_children_to_merge or cls._should_merge_elements(current_children_to_merge[0],
                                                                           root[child_index].tag):
                current_children_to_merge.append(root[child_index])
            else:
                # Found an item that cannot be part of the current group, searching stage done, merge the current group
                if len(current_children_to_merge) > 1:
                    for subgroup in generate_subgroups_as_lists(current_children_to_merge):
                        top_merged_element = cls._merge_side_of_group(subgroup, True)
                        if top_merged_element:
                            root.insert(child_index, top_merged_element)

                        bottom_merged_element = cls._merge_side_of_group(subgroup, False)
                        if bottom_merged_element:
                            root.insert(child_index + len(current_children_to_merge), top_merged_element)

                current_children_to_merge = [root[child_index]]

    def merge_conditional_elements(self):
        """
        Merges groups of subsequent elements that are the type but have mutually exclusive conditions.
        Creates a merged element before and after each merge group.
        """
        self._merge_conditional_elements(self.root)

    def format(self):
        self.remove_labels()
        self.format_conditions()
        # TODO: Improve removal so that it doesn't recursively remove all elements but removes them using a context
        #   So for example it won't remove all ImportGroup elements because that may mean something else in a special
        #   context of a tag we don't know about. Instead remove only ImportGroups that appear inside a Project tag.
        self.remove_empty_elements(["PropertyGroup", "ImportGroup", "ItemDefinitionGroup", "ClCompile", "Link",
                                    "ItemGroup"])
