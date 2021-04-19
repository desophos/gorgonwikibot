from operator import not_, truth

import pytest
from gorgonwikibot.content import Ability


@pytest.mark.parametrize(
    "result,data",
    [
        ("[[A]]", {"Name": "A"}),
        ("[[A]]", {"Name": "A", "Skill": "Unknown"}),
        ("[[B|A]]", {"Name": "A", "Skill": "B"}),
    ],
)
def test_link(dummy_ability, result, data):
    assert result == dummy_ability(custom=data).link


@pytest.mark.parametrize(
    "btest,data",
    [
        (not_, {}),
        (truth, {"AttributesThatDeltaPowerCost": []}),
        (truth, {"AttributesThatModPowerCost": []}),
        (truth, {"AttributesThatDeltaPowerCost": [], "AttributesThatModPowerCost": []}),
    ],
)
def test_is_player(dummy_ability, btest, data):
    assert btest(dummy_ability(custom=data).is_player)


@pytest.mark.parametrize(
    "btest,data",
    [
        (truth, {"InternalName": "xPet3"}),
        (not_, {"InternalName": "xPet3", "AttributesThatDeltaPowerCost": []}),
        (not_, {"InternalName": "PetUndeadArrow1"}),
        (not_, {"InternalName": "PetUndeadArrow2"}),
        (not_, {"InternalName": "PetUndeadOmegaArrow"}),
    ],
)
def test_is_pet(dummy_ability, btest, data):
    assert btest(dummy_ability(custom=data).is_pet)


@pytest.mark.parametrize(
    "btest,data",
    [
        (truth, {"InternalName": "MinigolemAoEHeal3"}),
        (not_, {"InternalName": "EnemyMinigolemPunch"}),
        (not_, {"InternalName": "MinigolemBombToss4"}),
    ],
)
def test_is_player_minigolem(dummy_ability, btest, data):
    assert btest(dummy_ability(custom=data).is_player_minigolem)


@pytest.mark.parametrize(
    "which,data",
    [
        (Ability.PetCommands.BASIC, {"Keywords": ["x", "PetBasicAttack", "y"]}),
        (Ability.PetCommands.SIC, {"Keywords": ["x", "PetA", "y"]}),
        (Ability.PetCommands.TRICK, {"Keywords": ["x", "PetB", "y"]}),
    ],
)
def test_which_pet_command(dummy_ability, which, data):
    assert which == dummy_ability(custom=data).which_pet_command


def test_no_pet_command(dummy_ability):
    with pytest.raises(ValueError):
        dummy_ability().which_pet_command
