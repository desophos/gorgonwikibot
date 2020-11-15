import pytest
from gorgonwikibot.content import Ability


@pytest.fixture
def dummy_ability():
    def _dummy(custom=None):
        data = {"Name": "_", "InternalName": "_", "Description": "_"}
        data.update(custom or {})
        return Ability("_", data)

    return _dummy
