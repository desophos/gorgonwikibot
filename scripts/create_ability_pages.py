import sys

import pywikibot
from gorgonwikibot.content import (Ability, Skill, get_all_content,
                                   get_content_by_id, get_name_from_iname)
from gorgonwikibot.entrypoint import entrypoint


def generate_infobox(a):
    def pluralize(n, unit):
        return f"{n} {unit}{'' if n == 1 else 's'}"

    def maybe_join(xs, sep=" "):
        return sep.join(filter(None, xs))

    s = [
        "{{Ability infobox",
        f"| name = {a.name}",
        f"| description = {a.data['Description']}",
        f"| level = {a.data['Level']}",
        f"| power cost = {a.data['PvE']['PowerCost']}",
        f"| reuse time = {a.data['ResetTime']}",
        f"| range = {a.data['PvE']['Range']} meters",
    ]

    try:
        skill = get_content_by_id(Skill, a.data["Skill"]).name
    except KeyError:
        skill = "Unknown"

    s.append(f"| skill = {skill}")

    if "Keywords" in a.data:
        s.append(
            "| keywords = " + " ".join("{{KWAB|%s}}" % s for s in a.data["Keywords"])
        )

    if "RageMultiplier" in a.data["PvE"]:
        s.append(f"| ragemulti = {a.data['PvE']['RageMultiplier']}")

    special = ""

    if "SpecialValues" in a.data["PvE"]:
        special = " ".join(
            maybe_join([v["Label"], str(v["Value"]), v["Suffix"]]) + "."
            for v in a.data["PvE"]["SpecialValues"]
        )

    if "SpecialInfo" in a.data:
        info = a.data["SpecialInfo"]
        special = maybe_join([special, info + ("" if info.endswith(".") else ".")])

    dots = None

    if "DoTs" in a.data["PvE"]:
        for dot in a.data["PvE"]["DoTs"]:
            if "SpecialRules" in dot and "BuffActivated" in dot["SpecialRules"]:
                pass
            elif "Preface" in dot:
                special = maybe_join(
                    [
                        special,
                        dot["Preface"],
                        str(dot["DamagePerTick"]),
                        dot["DamageType"],
                    ]
                )
            elif dot["DamagePerTick"] > 0:
                dots = " ".join(
                    [
                        str(dot["DamagePerTick"]),
                        str(dot["DamageType"]),
                        pluralize(dot["NumTicks"], "time"),
                        "over",
                        pluralize(dot["Duration"], "second"),
                    ]
                )

    damage = ""

    damage_amt = a.data["PvE"].get(
        "Damage", a.data["PvE"].get("HealthSpecificDamage", 0)
    )
    if damage_amt:
        damage = maybe_join(
            [
                str(damage_amt),
                a.data["DamageType"],
                "to health" if "HealthSpecificDamage" in a.data["PvE"] else "",
            ]
        )

    if dots:
        damage = f"{damage} initially and {dots}" if damage_amt else dots

    if damage:
        s.append(f"| damage = {damage}")

    if special:
        s.append(f"| special = {special}")

    s.append("}}")

    return "\n".join(s)


def generate_page(a):
    return "\n".join(
        [
            "__NOTOC__",
            generate_infobox(a),
            "<noinclude>[[Category:Abilities]]</noinclude>",
        ]
    )


def generate_pages():
    def is_learnable(a):
        keywords = a.data.get("Keywords")
        return "Lint_NotLearnable" not in keywords if keywords else True

    pages = {}

    for a in get_all_content(Ability):
        if (
            a.data.get("AttributesThatDeltaPowerCost")
            and is_learnable(a)
            or a.iname == "Punch"  # you start with this ability
        ):  # learnable player ability
            upgrade_of = a.data.get("UpgradeOf")
            if upgrade_of:
                text = f"#redirect [[{get_name_from_iname(Ability, upgrade_of)}]]"
            else:
                text = generate_page(a)

            pages[a.name] = text

    return pages


"""
{{Ability infobox
| name = Warmthball
| description = Throw a vaguely painful ball of warmth.
| skill = Fire Magic
| level = 0
| damage = 8 Fire
| power cost = 0
| reuse time = 2
| range = 30 meters
| ragemulti = 2
| special = {{Attribute|BOOST_SKILL_FIREMAGIC|+5}}
| keywords = <p>{{KWAB|Attack}}{{KWAB|FireMagic}}{{KWAB|Fireball}}{{KWAB|FireMagicAttack}}</p><p>{{KWAB|Ranged}}{{KWAB|BasicAttack}}{{KWAB|CombatRefresh}}{{KWAB|FireSpell}}</p>
}}"""


@entrypoint
def main(options):
    site = pywikibot.Site()
    for title, text in generate_pages().items():
        page = pywikibot.Page(site, title)
        if page.text == text:
            pywikibot.output(f"No changes to {title}\n")
            continue
        page.text = text
        if options.dry:
            pywikibot.output(f"{title}\n{page.text}\n")
        else:
            page.save(summary="Create ability page")


if __name__ == "__main__":
    main(sys.argv)
