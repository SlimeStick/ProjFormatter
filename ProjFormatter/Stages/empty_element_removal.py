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


def remove_empty_elements(root: ElementTree, remove_tags: list):
    """"
    An empty element is an element which either has no content or contains only empty elements.
    Elements with tags included in remove_tags are handled as empty elements.
    """
    mark_empty_elements_for_removal(root, remove_tags)
    remove_elements_marked_for_removal(root)
