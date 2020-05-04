import re
import sys

import pywikibot
from gorgonwikibot import cdn
from gorgonwikibot.content import (Ability, get_all_content,
                                   get_content_by_iname)
from gorgonwikibot.entrypoint import entrypoint


def is_player_minigolem(name):
    return "Minigolem" in name and "Enemy" not in name


def is_enemy(name):
    # no player pets or minigolems
    return not ("Pet" in name or is_player_minigolem(name))


def is_valid_enemy_ability(a):
    return (
        is_enemy(a.name)
        and "AttributesThatDeltaPowerCost" not in a.data  # no player abilities
        and a.data["Description"]  # we only care about abilities with tooltips
    )


def get_abilities(validator, include=[]):
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


def get_ais(validator):
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
    include = [
        "PetUndeadArrow1",
        # "PetUndeadArrow2",  # no description
        "PetUndeadOmegaArrow",
        "MinigolemBombToss4",
        "MinigolemPunch4",
        "MinigolemRageAcidToss4",
    ]  # special cases for SkeletonDistanceArcher and SecurityGolem

    abilities = get_abilities(is_valid_enemy_ability, include)
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


@entrypoint
def main(options):
    site = pywikibot.Site()
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
            page.save(summary="Create AI Profile page")


if __name__ == "__main__":
    main(sys.argv)
