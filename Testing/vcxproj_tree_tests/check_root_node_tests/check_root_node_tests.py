import pytest
from ProjFormatter.trees.vcxproj_tree import VCXProjTree


def test_illegal_root_node_missing_default_targets():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_root_node_missing_default_targets.vcxproj')


def test_illegal_root_node_namespace():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_root_node_missing_default_targets.vcxproj')


def test_illegal_root_node_tag():
    with pytest.raises(ValueError):
        VCXProjTree('test_illegal_root_node_missing_default_targets.vcxproj')


def test_legal_root_node():
    VCXProjTree('test_legal_root_node.vcxproj')
