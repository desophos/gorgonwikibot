import re
import sys
from functools import partial

import pywikibot
from gorgonwikibot import cdn
from gorgonwikibot.content import (Ability, Ai, get_all_content,
                                   get_content_by_iname)
from gorgonwikibot.entrypoint import entrypoint


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


def get_ais(validator=lambda _: True):
    return filter(validator, get_all_content(Ai))


def generate_ai_profiles():
    """'''AIP:Kraken'''
    : {{Combat Ability|KrakenBeak}}
    : {{Combat Ability|KrakenSlam}}
    : {{Combat Ability Rage|KrakenRage}}
    <noinclude>[[Category:AI Profile]]</noinclude>
    """

    abilities = get_abilities(lambda a: a.is_enemy and a.data["Description"])
    ais = get_ais(lambda ai: ai.is_enemy)
    profiles = {}

    for ai in ais:
        # ignore abilities that have already been filtered out
        alist = list(filter(lambda a: a in abilities, ai.abilities()))
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
            profiles[ai.name] = profile
    return profiles


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
