from defusedxml import ElementTree

from ProjFormatter.trees.vcxproj_tree import VCXProjTree

from ProjFormatter.tree_traversers.depth_first_traversal import DepthFirstTraverser


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
    vcxproj_tree = VCXProjTree(r'C:\Users\david\ProjFormatter\Testing\example.vcxproj')

    print(vcxproj_tree.get_project_configurations())
