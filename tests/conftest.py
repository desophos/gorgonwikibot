import pytest
from gorgonwikibot.content import Ability, Ai


@pytest.fixture
def dummy_ability():
    def _dummy(custom=None):
        data = {"Name": "_", "InternalName": "_", "Description": "_"}
        data.update(custom or {})
        return Ability("_", data)

    return _dummy


@pytest.fixture
def dummy_ai():
    def _dummy(id=None, custom=None):
        data = {"Abilities": {}}
        data.update(custom or {})
        return Ai(id or "_", data)

    return _dummy
