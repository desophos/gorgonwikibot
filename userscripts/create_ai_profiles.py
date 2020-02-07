import pywikibot
from scripts.userscripts.GorgonWiki.RemoteData import Cdn


def is_player_minigolem(name):
    return "Minigolem" in name and "Enemy" not in name


def validate_name(name):
    # no player pets or minigolems
    return not ("Pet" in name or is_player_minigolem(name))


def get_abilities(cdn):
    include = [
        "PetUndeadArrow1",
        "PetUndeadArrow2",
        "PetUndeadOmegaArrow",
        "MinigolemBombToss4",
        "MinigolemPunch4",
        "MinigolemRageAcidToss4",
    ]  # special cases for SkeletonDistanceArcher and SecurityGolem

    return {
        a["InternalName"]: {
            "Description": a["Description"],
            "IconID": a["IconID"],
            "Keywords": a.get("Keywords", []),
        }
        for a in cdn.get_file("abilities").values()
        if a["InternalName"] in include  # special cases
        or validate_name(a["InternalName"])
        and "AttributesThatDeltaPowerCost" not in a  # no player abilities
        and a["Description"]  # we only care about abilities with tooltips
    }


def get_ais(cdn):
    return {
        name: [
            ability
            for ability, params in v["Abilities"].items()
            if "minLevel" not in params  # ignore scaled abilities
        ]
        for name, v in cdn.get_file("ai").items()
        if validate_name(name)
    }


def generate_profiles(cdn):
    """'''AIP:Kraken'''
    : {{Combat Ability|KrakenBeak}}
    : {{Combat Ability|KrakenSlam}}
    : {{Combat Ability Rage|KrakenRage}}
    <noinclude>[[Category:AI Profile]]</noinclude>
    """
    ais = get_ais(cdn)
    abilities = get_abilities(cdn)
    profiles = {}
    for ai, alist in ais.items():
        profile = ""
        rages, nonrages = [], []
        for a in alist:
            if a in abilities:  # some abilities may have been filtered out
                if "RageAttack" in abilities[a]["Keywords"]:
                    rages.append(a)
                else:
                    nonrages.append(a)
        # we want all nonrages before all rages
        for a in nonrages:
            profile += f": {{{{Combat Ability|{a}}}}}\n"
        for a in rages:
            profile += f": {{{{Combat Ability Rage|{a}}}}}\n"
        profile += "<noinclude>[[Category:AI Profile]]</noinclude>"
        profiles[ai] = profile
    return profiles


def main(*args):
    cdn = Cdn()
    local_args = pywikibot.handle_args(args)
    dry_run = False

    for arg in local_args:
        option, sep, value = arg.partition(":")
        if option == "-dry-run":
            dry_run = True

    site = pywikibot.Site()
    for name, profile in generate_profiles(cdn).items():
        page = pywikibot.Page(site, f"AIP:{name}")
        page.text = profile
        if dry_run:
            pywikibot.output("Dry-run mode")
            pywikibot.output(f"AIP:{name}\n{page.text}\n")
        else:
            page.save(summary="Create AI Profile page")


if __name__ == "__main__":
    main()
