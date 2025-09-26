import os.path

from ProjFormatter.trees.vcxproj_tree import VCXProjTree

TEST_DIR = os.path.dirname(__file__)


def test_nothing_to_merge_conditional_elements():
    vcxproj_tree = VCXProjTree(os.path.join(TEST_DIR, 'test_nothing_to_merge_conditional_elements/input.xml'))

    vcxproj_tree.merge_conditional_elements()

    with open(os.path.join(TEST_DIR, 'test_nothing_to_merge_conditional_elements/expected_outcome.xml'),
              'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(vcxproj_tree)


def test_split_merge_conditional_elements():
    vcxproj_tree = VCXProjTree(os.path.join(TEST_DIR, 'test_split_merge_conditional_elements/input.xml'))

    vcxproj_tree.merge_conditional_elements()

    with open(os.path.join(TEST_DIR, 'test_split_merge_conditional_elements/expected_outcome.xml'), 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(vcxproj_tree)


def test_subgroups_merge_conditional_elements():
    vcxproj_tree = VCXProjTree(os.path.join(TEST_DIR, 'test_subgroups_merge_conditional_elements/input.xml'))

    vcxproj_tree.merge_conditional_elements()

    with open(os.path.join(TEST_DIR, 'test_subgroups_merge_conditional_elements/expected_outcome.xml'), 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(vcxproj_tree)
