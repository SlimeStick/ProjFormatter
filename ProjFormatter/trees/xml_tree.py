from ProjFormatter.utils.element_utils import get_children, is_empty_element, get_child_count, \
    are_elements_of_same_type, \
    merge_children, are_relevant_elements
from defusedxml import ElementTree
from lxml import etree


class XMLTree:
    def __init__(self, file_path: str):
        self.tree = ElementTree.parse(file_path)
        self.root = self.tree.getroot()
        self.__remove_namespace()

    def __remove_namespace(self):
        """
        Remove the namespace prefix from all tags in the tree.
        """
        for element in self.root.iter():
            element.tag = element.tag.split('}', 1)[1]

    def __convert_to_lxml(self, elem):
        """
        Recursively convert a defusedxml element to an lxml element.
        """
        # Create a new lxml element with the same tag and attributes
        lxml_elem = etree.Element(elem.tag, elem.attrib)

        # If the element has text, preserve it
        if elem.text and elem.text.strip():
            lxml_elem.text = elem.text.strip()

        # If the element has children, recurse through them
        for child in elem:
            lxml_child = self.__convert_to_lxml(child)
            lxml_elem.append(lxml_child)

        return lxml_elem

    def __str__(self):
        lxml_root = self.__convert_to_lxml(self.root)

        # Add back the xmlns namespace declaration to the root element
        lxml_root.attrib['xmlns'] = "http://schemas.microsoft.com/developer/msbuild/2003"

        # Pretty-print the XML tree using lxml's method
        return etree.tostring(
            lxml_root,
            pretty_print=True,
            doctype="<?xml version=\"1.0\" encoding=\"utf-8\"?>",
        ).decode('utf-8')

    def save_to_file(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(self))

    def remove_attributes(self, attribute_names: list[str]):
        """
        Removes specified attributes from all nodes in the XML tree.
        """
        if not attribute_names:
            return

        for element in self.root.iter():
            for attribute in attribute_names:
                if attribute in element.attrib:
                    del element.attrib[attribute]

    def remove_empty_elements(self, element_names: list):
        """"
        Removes an element if it has no tags and no content and is in the element_names list.
        Does not remove all empty elements because empty elements can have the meaning of resetting an attribute.
        """
        for parent in self.root.iter():
            for child in get_children(parent):
                if child.tag in element_names and is_empty_element(child):
                    parent.remove(child)

    @classmethod
    def __merge_elements_of_same_type(cls, root):
        for child in get_children(root):
            cls.__merge_elements_of_same_type(child)

        index = 0
        skip_index = 0

        while True:
            if index + 1 >= get_child_count(root):
                break
            if index + 1 + skip_index >= get_child_count(root):
                index += 1
                skip_index = 0

            child1 = root[index]
            child2 = root[index + 1 + skip_index]
            if are_elements_of_same_type(child1, child2):
                merge_children(root, child2, child1)
                # Don't increment index as one child2 was deleted
            else:
                if not are_relevant_elements(child1, child2):
                    skip_index += 1
                else:
                    index += 1
                    skip_index = 0

    def merge_elements_of_same_type(self):
        self.__merge_elements_of_same_type(self.root)
