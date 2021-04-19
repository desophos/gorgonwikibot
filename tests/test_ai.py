from operator import not_, truth

import pytest


@pytest.mark.parametrize(
    "btest,id", [(truth, "Minigolem_Beginner"), (not_, "EnemyMinigolem_Puncher")]
)
def test_is_player_minigolem(dummy_ai, btest, id):
    assert btest(dummy_ai(id=id).is_player_minigolem)


@pytest.mark.parametrize(
    "btest,id",
    [
        (truth, "BigCat_Pet"),
        (not_, "BigCat"),
    ],
)
def test_is_pet(dummy_ai, btest, id):
    assert btest(dummy_ai(id=id).is_pet)


@pytest.mark.parametrize(
    "btest,name,params",
    [
        (truth, "2", {}),
        (truth, "2", {"minLevel": 1}),
        (truth, "_", {"minLevel": 2}),
        (truth, "B_", {"minLevel": 2}),
        (not_, "2", {"minLevel": 2}),
        (not_, " D", {"minLevel": 200}),
    ],
)
def test_exclude_scaled(dummy_ai, btest, name, params):
    """Non-scaled abilities should be included, scaled ones should be excluded."""
    assert btest(name in dummy_ai(custom={"Abilities": {name: params}}).abilities())
