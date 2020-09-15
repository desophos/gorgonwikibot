from operator import not_, truth

import pytest
from gorgonwikibot.content import Ability
from scripts.create_ai_profiles import (get_abilities, get_ais, is_enemy,
                                        is_player_minigolem, is_scaled,
                                        is_valid_enemy_ability)


def dummy_ability(custom={}):
    data = {"Name": "_", "InternalName": "_", "Description": "_"}
    data.update(custom)
    return Ability("_", data)


@pytest.mark.parametrize(
    "btest,data", [(truth, "Minigolem_Beginner"), (not_, "EnemyMinigolem_Puncher")]
)
def test_is_player_minigolem(btest, data):
    assert btest(is_player_minigolem(data))


@pytest.mark.parametrize(
    "btest,data",
    [
        (not_, "Minigolem_Beginner"),
        (truth, "EnemyMinigolem_Puncher"),
        (not_, "BigCat_Pet"),
        (truth, "BigCat"),
    ],
)
def test_is_enemy(btest, data):
    assert btest(is_enemy(data))


@pytest.mark.parametrize(
    "btest,data",
    [(not_, {"AttributesThatDeltaPowerCost": []}), (not_, {"Description": ""})],
)
def test_is_valid_enemy_ability(btest, data):
    assert btest(is_valid_enemy_ability(dummy_ability(data)))


@pytest.mark.parametrize(
    "btest,name,data",
    [
        (not_, "2", {}),
        (not_, "2", {"minLevel": 1}),
        (not_, "_", {"minLevel": 2}),
        (not_, "B_", {"minLevel": 2}),
        (truth, "2", {"minLevel": 2}),
        (truth, " D", {"minLevel": 200}),
    ],
)
def test_is_scaled(btest, name, data):
    assert btest(is_scaled(name, data))


def test_get_abilities():
    abilities = get_abilities(is_valid_enemy_ability)
    assert abilities


def test_get_ais():
    ais = get_ais(is_enemy)
    assert ais
    assert all(is_enemy(ai) for ai in ais)
