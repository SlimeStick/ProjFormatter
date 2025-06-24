from ProjFormatter.stages.remove_attributes import remove_attributes
from ProjFormatter.trees.xml_tree import XMLTree


def test_remove_attributes_sanity():
    xml_tree = XMLTree('test_remove_attributes_sanity_files/input.xml')

    remove_attributes(xml_tree.root, ["Label"])

    with open('test_remove_attributes_sanity_files/expected_outcome.xml', 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)


def test_attributes_to_remove_do_not_appear_in_tree():
    xml_tree = XMLTree('test_attributes_to_remove_do_not_appear_in_tree_files/input.xml')

    remove_attributes(xml_tree.root, ["Include"])

    with open('test_attributes_to_remove_do_not_appear_in_tree_files/expected_outcome.xml', 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)
