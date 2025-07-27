import os.path

import pytest

from ProjFormatter.trees.vcxproj_tree import VCXProjTree

TEST_DIR = os.path.dirname(__file__)


def test_illegal_missing_microsoft_cpp_props():
    with pytest.raises(ValueError):
        VCXProjTree(os.path.join(TEST_DIR, 'test_illegal_missing_microsoft_cpp_props.vcxproj'))


def test_legal_microsoft_cpp_props():
    VCXProjTree(os.path.join(TEST_DIR, 'test_legal_microsoft_cpp_props.vcxproj'))
