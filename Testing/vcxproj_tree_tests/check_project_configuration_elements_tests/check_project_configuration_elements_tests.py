import pytest

from ProjFormatter.trees.vcxproj_tree import VCXProjTree


def test_illegal_project_configuration_missing_configuration():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_missing_configuration.vcxproj')


def test_illegal_project_configuration_missing_include():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_missing_include.vcxproj')


def test_illegal_project_configuration_missing_platform():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_missing_platform.vcxproj')


def test_illegal_project_configuration_too_few_children():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_too_few_children.vcxproj')


def test_illegal_project_configuration_too_many_children():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_configuration_too_many_children.vcxproj')


def test_legal_project_configuration():
    VCXProjTree('test_legal_project_configuration.vcxproj')
