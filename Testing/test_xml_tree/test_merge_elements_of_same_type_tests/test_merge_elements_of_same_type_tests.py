import os.path

from ProjFormatter.trees.xml_tree import XMLTree

TEST_DIR = os.path.dirname(__file__)


def test_sanity_merge_elements_of_same_type():
    xml_tree = XMLTree(os.path.join(TEST_DIR, 'test_sanity_merge_elements_of_same_type_files/input.xml'))

    xml_tree.merge_elements_of_same_type()

    with open(os.path.join(TEST_DIR, 'test_sanity_merge_elements_of_same_type_files/expected_outcome.xml'), 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)


def test_skip_irrelevant_elements():
    xml_tree = XMLTree(os.path.join(TEST_DIR, 'test_skip_irrelevant_elements_files/input.xml'))

    xml_tree.merge_elements_of_same_type()

    with open(os.path.join(TEST_DIR, 'test_skip_irrelevant_elements_files/expected_outcome.xml'), 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)
