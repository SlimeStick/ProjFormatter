from ProjFormatter.tree_traversers.level_order_traversal import LevelOrderTraverser
from ProjFormatter.trees.xml_tree import XMLTree

from ProjFormatter.utils.element_utils import get_children


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

    def get_project_configurations(self):
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
            if child.attrib["Project"] == "$(VCTargetsPath)\Microsoft.Cpp.Default.props":
                return
        raise ValueError("Microsoft.Cpp.Default.props wasn't imported")

    def check_microsoft_cpp_props(self):
        """
        Makes sure that Microsoft.Cpp.props is imported.
        """
        for child in get_children(self.root):
            if child.tag != 'Import':
                continue
            if child.attrib["Project"] == "$(VCTargetsPath)\Microsoft.Cpp.props":
                return
        raise ValueError("Microsoft.Cpp.props wasn't imported")

    def check_format_sanity(self):
        """
        Makes sure that the tree is in the vcxproj format.
        Should be called after editing the tree as according to Microsoft's documentation, manual editing mistakes can
        cause the IDE to crash or behave in unexpected ways.
        Implemented so that format testing can be done without running MSBuild to check for mistakes and because even
        MSBuild doesn't enforce all rules specified by Microsoft.
        """
        self.check_include_sanity()
        self.check_project_configuration_elements()
        self.check_project_configuration_combinations()
        self.check_root_node()
        self.check_import_elements()
        self.check_microsoft_cpp_default_props()
        self.check_microsoft_cpp_props()

        # More stuff we could check:
        #   . That ~stuff~ isn't used before Microsoft.Cpp.default.props is imported
        #   . That ~stuff~ isn't used before Microsoft.Cpp.props is imported
        #   . That UserMacros don't change between configurations
        #   . Understand how TF Per-configuration PropertyGroup elements work
        #   . Understand how TF Per-configuration ItemDefinitionGroup elements work
        #   . Make sure that ItemGroup elements don't have conditions on them
        #   . Maybe make sure that settings in ItemGroup elements are replicated for each configuration? WTF?
        #   . Check that Include statements don't have wildcards or macros
        #   . Make sure that references don't have conditions
        #   . Make sure that reference metadata don't have conditions

    def remove_labels(self):
        """
        Removes all Labels as any Label attributes are arbitrary tags that are only used by Visual Studio as signposts
        for editing; they have no other function.
        """
        self.remove_attributes(["Label"])

    def format(self):
        self.remove_labels()
        self.remove_empty_elements(["PropertyGroup", "ImportGroup", "ItemDefinitionGroup", "ClCompile", "Link",
                                    "ItemGroup"])
