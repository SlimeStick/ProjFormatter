import os.path

from ProjFormatter.trees.msbuild_tree import MSBuildTree

TEST_DIR = os.path.dirname(__file__)


def test_whitespace_in_condition():
    msbuild_tree = MSBuildTree(os.path.join(TEST_DIR, 'test_whitespace_in_condition/input.xml'))

    msbuild_tree.format_conditions()

    with open(os.path.join(TEST_DIR, 'test_whitespace_in_condition/expected_outcome.xml'),
              'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(msbuild_tree)
