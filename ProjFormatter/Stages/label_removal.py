def remove_attributes(root, attributes_to_remove):
    """
    Removes specified attributes from all nodes in the XML tree.
    """
    for element in root.iter():
        for attribute in attributes_to_remove:
            if attribute in element.attrib:
                del element.attrib[attribute]
