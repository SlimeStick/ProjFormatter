from ProjFormatter.element_utils import get_children, is_empty_element
from defusedxml import ElementTree


def remove_empty_elements(root: ElementTree, element_names: list):
    """"
    Removes an element if it has no tags and no content and is in the element_names list.
    Does not remove all empty elements because empty elements in vcxproj format can have the meaning to reset an
    attribute.
    """
    for parent in root.iter():
        for child in get_children(parent):
            if child.tag in element_names and is_empty_element(child):
                parent.remove(child)
