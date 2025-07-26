from ProjFormatter.trees.xml_tree import XMLTree


def test_sanity_remove_empty_elements():
    xml_tree = XMLTree('test_sanity_remove_empty_elements_files/input.xml')

    xml_tree.remove_empty_elements(["ImportGroup"])

    with open('test_sanity_remove_empty_elements_files/expected_outcome.xml', 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)


def test_empty_element_not_in_element_list():
    xml_tree = XMLTree('test_empty_element_not_in_element_list_files/input.xml')

    xml_tree.remove_empty_elements(["NonExistentGroup"])

    with open('test_empty_element_not_in_element_list_files/expected_outcome.xml', 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)


def test_no_empty_elements():
    xml_tree = XMLTree('test_no_empty_elements_files/input.xml')

    xml_tree.remove_empty_elements(["ImportGroup"])

    with open('test_no_empty_elements_files/expected_outcome.xml', 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(xml_tree)
