import pytest
from ProjFormatter.trees.vcxproj_tree import VCXProjTree


def test_illegal_missing_microsoft_cpp_default_props():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_missing_microsoft_cpp_default_props.vcxproj')


def test_legal_microsoft_cpp_default_props():
    VCXProjTree('test_legal_microsoft_cpp_default_props.vcxproj')
