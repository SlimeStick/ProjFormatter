from ProjFormatter.tree_traversers.level_order_traversal import LevelOrderTraverser
from ProjFormatter.trees.xml_tree import XMLTree


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

    def get_project_configurations(self):
        project_configurations = []
        for element in LevelOrderTraverser(self.root, 2):
            if element.tag == 'ProjectConfiguration':
                project_configurations.append(element.attrib["Include"])
        return project_configurations

    def check_project_configurations(self):
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

    def check_format_sanity(self):
        """
        Makes sure that the tree is in the vcxproj format.
        Should be called after editing the tree as according to Microsoft's documentation, manual editing mistakes can
        cause the IDE to crash or behave in unexpected ways.

        :param check_wildcards: Whether to check for wildcard usage in elements.
        :param check_lists: Whether to check for list usage in elements.
        :param check_order: Whether to validate elements order.
        :param check_macros: Whether to check for macro usage in project item paths.
        :param check_targets: Whether to check that all targets are imported at the end of the file.
        """
        # There are 2 types of rules we check
        # 1. Rules that apply to all elements no matter where they are
        # 2. Order rules

        # First we check the general rules that apply to all elements
        self.check_include_sanity()
        self.check_project_configurations()

        # Then we check the rules about the order of elements

    def remove_labels(self):
        """
        Removes all Labels as any Label attributes are arbitrary tags that are only used by Visual Studio as signposts
        for editing; they have no other function.
        """
        self.remove_attributes(["Label"])

    def format(self):
        safe_empty_elements_to_remove = ["PropertyGroup", "ImportGroup", "ItemDefinitionGroup", "ClCompile", "Link",
                                         "ItemGroup"]
