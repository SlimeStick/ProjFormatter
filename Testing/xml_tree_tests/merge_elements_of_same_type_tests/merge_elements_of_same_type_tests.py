from ProjFormatter.trees.xml_tree import XMLTree


def test_sanity_merge_elements_of_same_type():
    xml_tree = XMLTree('test_sanity_merge_elements_of_same_type/input.xml')

    xml_tree.merge_elements_of_same_type()

    with open('test_sanity_merge_elements_of_same_type/expected_outcome.xml', 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)


def test_skip_irrelevant_elements():
    xml_tree = XMLTree('test_skip_irrelevant_elements/input.xml')

    xml_tree.merge_elements_of_same_type()

    with open('test_skip_irrelevant_elements/expected_outcome.xml', 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)
