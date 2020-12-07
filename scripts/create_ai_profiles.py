import re
import sys
from functools import partial

import pywikibot
from gorgonwikibot import cdn
from gorgonwikibot.content import (Ability, get_all_content,
                                   get_content_by_iname)
from gorgonwikibot.entrypoint import entrypoint


def is_player_minigolem(name):
    return "Minigolem" in name and "Enemy" not in name


def is_pet(name):
    return "Pet" in name


def is_enemy(name):
    include = [
        "PetUndeadArrow1",
        # "PetUndeadArrow2",  # no description
        "PetUndeadOmegaArrow",
        "MinigolemBombToss4",
        "MinigolemPunch4",
        "MinigolemRageAcidToss4",
    ]  # special cases for SkeletonDistanceArcher and SecurityGolem

    # no player pets or minigolems
    return name in include or not (is_pet(name) or is_player_minigolem(name))


def is_valid_ability(a, validator=lambda _: True):
    return (
        validator(a.iname)
        and "AttributesThatDeltaPowerCost" not in a.data  # no player abilities
        and a.data["Description"]  # we only care about abilities with tooltips
    )


def get_abilities(validator=lambda _: True, include=[]):
    return {
        a.iname: {
            "Description": a.data["Description"],
            "IconID": a.data["IconID"],
            "Keywords": a.data.get("Keywords", []),
        }
        for a in get_all_content(Ability)
        if a.iname in include or validator(a)
    }


def is_scaled(name, params):
    # some abilities have duplicates scaled to higher levels
    return (
        "minLevel" in params
        and params["minLevel"] > 1  # SnailRage and SpiderKill
        and re.search(r"[B-Z2-9]$", name)
    )


def get_ais(validator=lambda _: True):
    return {
        name: [
            ability
            for ability, params in v["Abilities"].items()
            if not is_scaled(ability, params)
        ]
        for name, v in cdn.get_file("ai").items()
        if validator(name)
    }


def generate_ai_profiles():
    """'''AIP:Kraken'''
    : {{Combat Ability|KrakenBeak}}
    : {{Combat Ability|KrakenSlam}}
    : {{Combat Ability Rage|KrakenRage}}
    <noinclude>[[Category:AI Profile]]</noinclude>
    """

    abilities = get_abilities(partial(is_valid_ability, validator=is_enemy))
    ais = get_ais(is_enemy)
    profiles = {}

    for ai, alist in ais.items():
        # ignore abilities that have already been filtered out
        alist = list(filter(lambda a: a in abilities, alist))
        if alist:  # ai has at least one valid ability
            profile = ""
            rages, nonrages = [], []
            for a in alist:
                if "RageAttack" in abilities[a]["Keywords"]:
                    rages.append(a)
                else:
                    nonrages.append(a)
            # we want all nonrages before all rages
            for a in nonrages:
                profile += ": {{Combat Ability|%s}}\n" % a
            for a in rages:
                profile += ": {{Combat Ability Rage|%s}}\n" % a
            profile += "<noinclude>[[Category:AI Profile]]</noinclude>"
            profiles[ai] = profile
    return profiles


def generate_pet_profiles():
    """
    {|
    |-
    |rowspan="3"|{{Combat Ability icon|BearBite}}
    |'''Bear Claw (Pet)'''
    |-
    |Slashing Damage
    |-
    |Base Damage: X
    |}"""
    abilities = get_abilities(lambda s: "(Pet)" in s)
    ais = get_ais(lambda s: "_Pet" in s)
    profiles = {}

    for ai, alist in ais.items():
        # ignore abilities that have already been filtered out
        # and get Ability instances from the ai ability list
        alist = list(map(get_content_by_iname, filter(lambda a: a in abilities, alist)))
        if alist:  # ai has at least one valid ability
            profile = ""
            for a in alist:
                profile += "\n".join(
                    "{|",
                    "|-",
                    '|rowspan="3"|{{Combat Ability icon|%s}}' % a.iname,
                    "'''%s'''" % a.name,
                    "|-",
                    "|%s" % a.data["Description"],
                    "|-",
                    "|Base Damage: %i" % a.data["PvE"]["Damage"],
                    "|}",
                )


@entrypoint
def main(site, options):
    for name, profile in generate_ai_profiles().items():
        title = f"AIP:{name}"
        page = pywikibot.Page(site, title)
        if page.text == profile:
            pywikibot.output(f"No changes to {title}\n")
            continue
        page.text = profile
        if options.dry:
            pywikibot.output(f"{title}\n{page.text}\n")
        else:
            page.save(summary=options.msg or "Create AI Profile page")


if __name__ == "__main__":
    main(sys.argv)
