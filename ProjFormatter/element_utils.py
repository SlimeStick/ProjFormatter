import re
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


def merge_children(root, source, destination):
    transfer_children(source, destination)
    root.remove(source)


def are_elements_equal(elements: list[ElementTree]) -> bool:
    first = elements[0]
    first_tostring = ElementTree.tostring(first)

    return all(
        elem.tag == first.tag and
        elem.attrib == first.attrib and
        ElementTree.tostring(elem) == first_tostring
        for elem in elements
    )


def are_elements_of_same_type(element1, element2):
    return element1.attrib == element2.attrib and element1.tag == element2.tag

def are_relevant_elements(element1, element2, configurations=None, platforms=None):
    """
    Returns whether either element can affect the other.
    Currently, doesn't evaluate XML properties so it's best-effort based on known cases of the Condition attribute.
    """
    if configurations is None:
        configurations = ["Debug", "Release"]

    if platforms is None:
        platforms = ["x64", "Win32"]

    configurations = "|".join(configurations)
    platforms = "|".join(platforms)

    pattern = r"^'\$\((Configuration)\)\|\$\((Platform)\)'==('({})\|({})')$".format(configurations, platforms)
    if re.match(pattern, element1.attrib.get("Condition", "")) is None:
        return True

    if re.match(pattern, element2.attrib.get("Condition", "")) is None:
        return True

    return element1.attrib["Condition"] == element2.attrib["Condition"]
