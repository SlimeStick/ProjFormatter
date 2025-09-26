import os.path

import pytest

from ProjFormatter.trees.msbuild_tree import MSBuildTree

TEST_DIR = os.path.dirname(__file__)


def test_illegal_root_node_namespace():
    with pytest.raises(ValueError):
        MSBuildTree(os.path.join(TEST_DIR, 'test_illegal_root_node_namespace.vcxproj'))


def test_illegal_root_node_tag():
    with pytest.raises(ValueError):
        MSBuildTree(os.path.join(TEST_DIR, 'test_illegal_root_node_tag.vcxproj'))


def test_legal_root_node():
    MSBuildTree(os.path.join(TEST_DIR, 'test_legal_root_node.vcxproj'))
