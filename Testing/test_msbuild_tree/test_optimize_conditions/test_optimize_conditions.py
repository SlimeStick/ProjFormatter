import os.path

from ProjFormatter.trees.msbuild_tree import MSBuildTree

TEST_DIR = os.path.dirname(__file__)


def test_optimize_conditions_all_possible_values_known_expand_not_equals():
    msbuild_tree = MSBuildTree(
        os.path.join(TEST_DIR, 'test_optimize_conditions_all_possible_values_known_expand_not_equals/input.xml'))

    msbuild_tree.optimize_conditions(possible_values={"Platform": ["x64", "Win32", "ARM"]})

    with open(os.path.join(TEST_DIR,
                           'test_optimize_conditions_all_possible_values_known_expand_not_equals/expected_outcome.xml'),
              'r') as file:
        expected_outcome = file.read()


    assert expected_outcome == str(msbuild_tree)


def test_optimize_conditions_all_possible_values_known_redundant_not_equals():
    msbuild_tree = MSBuildTree(
        os.path.join(TEST_DIR, 'test_optimize_conditions_all_possible_values_known_redundant_not_equals/input.xml'))

    msbuild_tree.optimize_conditions(possible_values={"Platform": ["x64", "Win32"]})

    with open(os.path.join(TEST_DIR,
                           'test_optimize_conditions_all_possible_values_known_redundant_not_equals/expected_outcome.xml'),
              'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(msbuild_tree)


def test_optimize_conditions_and():
    msbuild_tree = MSBuildTree(os.path.join(TEST_DIR, 'test_optimize_conditions_and/input.xml'))

    msbuild_tree.optimize_conditions()

    with open(os.path.join(TEST_DIR, 'test_optimize_conditions_and/expected_outcome.xml'), 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(msbuild_tree)


def test_optimize_conditions_not_all_possible_values_known():
    msbuild_tree = MSBuildTree(
        os.path.join(TEST_DIR, 'test_optimize_conditions_not_all_possible_values_known/input.xml'))

    msbuild_tree.optimize_conditions()

    with open(os.path.join(TEST_DIR, 'test_optimize_conditions_not_all_possible_values_known/expected_outcome.xml'),
              'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(msbuild_tree)


def test_optimize_conditions_or():
    msbuild_tree = MSBuildTree(os.path.join(TEST_DIR, 'test_optimize_conditions_or/input.xml'))

    msbuild_tree.optimize_conditions()

    with open(os.path.join(TEST_DIR, 'test_optimize_conditions_or/expected_outcome.xml'), 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(msbuild_tree)


def test_optimize_conditions_paranthesis():
    msbuild_tree = MSBuildTree(os.path.join(TEST_DIR, 'test_optimize_conditions_paranthesis/input.xml'))

    msbuild_tree.optimize_conditions()

    with open(os.path.join(TEST_DIR, 'test_optimize_conditions_paranthesis/expected_outcome.xml'), 'r') as file:
        expected_outcome = file.read()

    assert expected_outcome == str(msbuild_tree)
