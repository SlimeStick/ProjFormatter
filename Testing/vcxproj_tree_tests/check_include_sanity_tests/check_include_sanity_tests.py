import pytest
from ProjFormatter.trees.vcxproj_tree import VCXProjTree


def test_illegal_include():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_include.vcxproj')


def test_legal_include():
    VCXProjTree('test_legal_include.vcxproj')
