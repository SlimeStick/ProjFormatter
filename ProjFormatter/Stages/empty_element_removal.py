from defusedxml import ElementTree

MARKED_FOR_REMOVAL_ATTRIBUTE = 'ProjFormatter_marked_for_removal'


def is_empty_element(element: ElementTree) -> bool:
    # len returns the number of child elements
    if len(element) != 0:
        return False

    # If there's any content inside the element besides white characters
    if element.text is not None and element.text.strip():
        return False

    return True


def mark_element_for_removal(element: ElementTree):
    element.set(MARKED_FOR_REMOVAL_ATTRIBUTE, 'True')


def mark_empty_elements_for_removal(root: ElementTree, remove_tags: list):
    for element in root.iter():
        if element.tag in remove_tags and is_empty_element(element):
            mark_element_for_removal(element)


def remove_elements_marked_for_removal(root: ElementTree):
    for parent in root.iter():
        for child in list(parent):
            if child.attrib.get(MARKED_FOR_REMOVAL_ATTRIBUTE) == 'True':
                parent.remove(child)


def remove_empty_elements(root: ElementTree, element_names: list):
    """"
    Removes an element if it has not tags and no content and is in the element_names list.
    Does not remove all empty elements because empty elements in vcxproj format can have the meaning to reset an
    attribute.
    """
    mark_empty_elements_for_removal(root, element_names)
    remove_elements_marked_for_removal(root)
