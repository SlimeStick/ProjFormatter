import pytest
from ProjFormatter.trees.vcxproj_tree import VCXProjTree


def test_illegal_import_elements_missing_project():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_import_elements_missing_project.vcxproj')


def test_legal_import_elements():
    VCXProjTree('test_legal_import_elements.vcxproj')
