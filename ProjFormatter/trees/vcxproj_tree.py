from ProjFormatter.tree_traversers.level_order_traversal import LevelOrderTraverser
from ProjFormatter.trees.msbuild_tree import MSBuildTree
from ProjFormatter.utils.element_utils import get_children


class VCXProjTree(MSBuildTree):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.check_format_sanity()

    def check_root_node(self):
        super().check_root_node()
        if "DefaultTargets" not in self.root.attrib:
            raise ValueError("The DefaultTargets attribute must be defined")

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

    def check_import_elements(self):
        """
        Makes sure that all Import elements are valid.
        """
        # TODO: Check if we need to just check in BFS level 2 or in all levels
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
        super().check_format_sanity()

        # TODO: Understand how many projects have $ in include statements
        self.check_include_sanity()
        self.check_project_configuration_elements()
        self.check_project_configuration_combinations()
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

    def format(self):
        self.remove_labels()
        self.format_conditions()
        # TODO: Improve removal so that it doesn't recursively remove all elements but removes them using a context
        #   So for example it won't remove all ImportGroup elements because that may mean something else in a special
        #   context of a tag we don't know about. Instead remove only ImportGroups that appear inside a Project tag.
        self.remove_empty_elements(["PropertyGroup", "ImportGroup", "ItemDefinitionGroup", "ClCompile", "Link",
                                    "ItemGroup"])
