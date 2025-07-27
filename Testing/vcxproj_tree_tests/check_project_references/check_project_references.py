import pytest

from ProjFormatter.trees.vcxproj_tree import VCXProjTree


def test_illegal_project_reference_conditional_metadata():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_reference_conditional_metadata.vcxproj')


def test_illegal_project_reference_conditional_reference():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_reference_conditional_reference.vcxproj')


def test_illegal_project_reference_missing_include():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_project_reference_missing_include.vcxproj')


def test_legal_project_reference():
    VCXProjTree('test_legal_project_reference.vcxproj')
