from ProjFormatter.trees.xml_tree import XMLTree

from ProjFormatter.tree_traversers.level_order_traversal import LevelOrderTraverser


class VCXProjTree(XMLTree):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.check_format_sanity()

    def get_project_configurations(self):
        for element in LevelOrderTraverser(self.root, 2):
            if element.tag == 'ProjectConfiguration':
                print(element)


    def check_format_sanity(
        self,
        check_wildcards: bool = True,
        check_lists: bool = True,
        check_order: bool = True,
        check_macros: bool = True,
        check_targets: bool = True
    ):
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
        pass

    def format(self):
        safe_empty_elements_to_remove = ["PropertyGroup", "ImportGroup", "ItemDefinitionGroup", "ClCompile", "Link",
                                         "ItemGroup"]
        pass
