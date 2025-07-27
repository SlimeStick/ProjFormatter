import os.path

import pytest

from ProjFormatter.trees.vcxproj_tree import VCXProjTree

TEST_DIR = os.path.dirname(__file__)


def test_illegal_project_configurations_configuration():
    with pytest.raises(ValueError):
        VCXProjTree(os.path.join(TEST_DIR, 'test_illegal_project_configuration_combinations.vcxproj'))


def test_legal_include():
    VCXProjTree(os.path.join(TEST_DIR, 'test_legal_project_configuration_combinations.vcxproj'))
