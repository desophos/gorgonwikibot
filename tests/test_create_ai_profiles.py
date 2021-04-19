from operator import not_, truth

import pytest
from scripts.create_ai_profiles import get_abilities, get_ais


def test_get_abilities():
    assert get_abilities()


def test_get_ais():
    assert get_ais()
