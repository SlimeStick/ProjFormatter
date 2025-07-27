import pytest

from ProjFormatter.trees.vcxproj_tree import VCXProjTree


def test_illegal_project_configuration_missing_configuration():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_missing_configuration.xml')


def test_illegal_project_configuration_missing_include():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_missing_include.xml')


def test_illegal_project_configuration_missing_platform():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_missing_platform.xml')


def test_illegal_project_configuration_too_few_children():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_too_few_children.xml')


def test_illegal_project_configuration_too_many_children():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_too_many_children.xml')


def test_legal_project_configuration():
    VCXProjTree('test_legal_project_configuration.xml')
