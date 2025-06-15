def remove_attributes(root, attribute_names):
    """
    Removes specified attributes from all nodes in the XML tree.
    """
    if not attribute_names:
        return

    for element in root.iter():
        for attribute in attribute_names:
            if attribute in element.attrib:
                del element.attrib[attribute]
