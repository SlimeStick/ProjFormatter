from defusedxml import ElementTree
from lxml import etree

class XMLTree:
    def __init__(self, file_path: str):
        self.tree = ElementTree.parse(file_path)
        self.root = self.tree.getroot()
        self.__remove_namespace(self.root)

    @staticmethod
    def __remove_namespace(root):
        """
        Remove the namespace prefix from all tags in the tree.
        """
        for element in root.iter():
            element.tag = element.tag.split('}', 1)[-1]

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

    def write_to_file(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(self))
