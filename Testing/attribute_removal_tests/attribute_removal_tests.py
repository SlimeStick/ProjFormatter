from ProjFormatter.xml_tree import XMLTree
from ProjFormatter.stages.attribute_removal import remove_attributes


def test_sanity():
    xml_tree = XMLTree('input.vcxproj')

    remove_attributes(xml_tree.root, ["Label"])

    with open('expected_outcome.vcxproj', 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)
