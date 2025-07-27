import os.path

import pytest

from ProjFormatter.trees.vcxproj_tree import VCXProjTree

TEST_DIR = os.path.dirname(__file__)


def test_illegal_import_elements_missing_project():
    with pytest.raises(ValueError):
        VCXProjTree(os.path.join(TEST_DIR, 'test_illegal_import_elements_missing_project.vcxproj'))


def test_legal_import_elements():
    VCXProjTree(os.path.join(TEST_DIR, 'test_legal_import_elements.vcxproj'))
