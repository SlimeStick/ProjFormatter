import pytest
from ProjFormatter.trees.vcxproj_tree import VCXProjTree


def test_illegal_project_configurations_configuration():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_combinations.xml')


def test_legal_include():
    VCXProjTree('test_legal_project_configuration_combinations.xml')
