import os.path

from ProjFormatter.trees.xml_tree import XMLTree

TEST_DIR = os.path.dirname(__file__)


def test_remove_attributes_sanity():
    xml_tree = XMLTree(os.path.join(TEST_DIR, 'test_remove_attributes_sanity_files/input.xml'))

    xml_tree.remove_attributes(["Label"])

    with open(os.path.join(TEST_DIR, 'test_remove_attributes_sanity_files/expected_outcome.xml'), 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)


def test_attributes_to_remove_do_not_appear_in_tree():
    xml_tree = XMLTree(os.path.join(TEST_DIR, 'test_attributes_to_remove_do_not_appear_in_tree_files/input.xml'))

    xml_tree.remove_attributes(["Include"])

    with open(os.path.join(TEST_DIR, 'test_attributes_to_remove_do_not_appear_in_tree_files/expected_outcome.xml'),
              'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)
