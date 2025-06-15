from defusedxml import ElementTree


def is_empty_element(element: ElementTree) -> bool:
    # len returns the number of child elements
    if len(element) != 0:
        return False

    # If there's any content inside the element besides white characters
    if element.text is not None and element.text.strip():
        return False

    return True


def remove_empty_elements(root: ElementTree, element_names: list):
    """"
    Removes an element if it has no tags and no content and is in the element_names list.
    Does not remove all empty elements because empty elements in vcxproj format can have the meaning to reset an
    attribute.
    """
    for parent in root.iter():
        for child in list(parent):
            if child.tag in element_names and is_empty_element(child):
                parent.remove(child)
