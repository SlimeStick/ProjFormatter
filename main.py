from defusedxml import ElementTree

from stages.attribute_removal import remove_attributes
from tree_traversers.level_order_traversal import LevelOrderTraverser
from stages.empty_element_removal import remove_empty_elements
from xml_tree.xml_tree import XMLTree


def merge_conditional_elements_by_tag(element: ElementTree, tag: str):
    """
    for each tag name:
        find no condition tag, if doesn't exist (all tags have condition), create it
        find tags common to all condition tags
        Remove them from all tags and put them in the no condition tag

    problem: it's ok to have 1 tag with a condition, like exists() so I must accept which conditions to "ignore" -> im allowed to merge
    """
    pass


def merge_conditional_elements(element: ElementTree, condition):
    """
    Flow is:
    For each tag name in the children:
     i.e. "Import, PropertyGroup, ItemGroup"
    Call merge_conditional_tag_by_name
    """
    tags = set([child.tag for child in element])
    for tag in tags:
        merge_conditional_elements_by_tag(element, tag)


if __name__ == "__main__":
    # xml_tree = XMLTree('simple_example.vcxproj')
    #
    # remove_attributes(xml_tree.root, ["Label"])
    # # remove_empty_elements(xml_tree.root, ["ImportGroup"])
    #
    # xml_tree.write_to_file('cleaned_file.xml')
    #
    # print(xml_tree)

    # for element in LevelOrderTraverser(root):
    # if element.tag == "{http://schemas.microsoft.com/developer/msbuild/2003}ProjectConfiguration":
    #     root.remove(element)
    # cleanup_namespace()
    pass