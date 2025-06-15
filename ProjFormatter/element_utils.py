from defusedxml import ElementTree


def get_child_count(element):
    return len(element)


def get_children(element):
    return list(element)


def is_empty_element(element: ElementTree) -> bool:
    if get_child_count(element) != 0:
        return False

    # If there's any content inside the element besides white characters
    if element.text is not None and element.text.strip():
        return False

    return True


def transfer_children(source, destination):
    children = get_children(source)
    for child in children:
        source.remove(child)
        destination.append(child)

def are_elements_equal(elements: list[ElementTree]) -> bool:
    first = elements[0]
    first_tostring = ElementTree.tostring(first)

    return all(
        elem.tag == first.tag and
        elem.attrib == first.attrib and
        ElementTree.tostring(elem) == first_tostring
        for elem in elements
    )
