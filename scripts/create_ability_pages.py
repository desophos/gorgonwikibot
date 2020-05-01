import sys

import pywikibot
from gorgonwikibot.content import Ability, get_all_content
from gorgonwikibot.entrypoint import entrypoint


def add_line(s, line):
    return "\n".join([s, line])


def generate_infobox(a):
    s = "\n".join(
        [
            "{{Ability infobox",
            f"| name = {a.name}",
            f"| description = {a.data['Description']}",
            f"| skill = {a.data['Skill']}",
            f"| level = {a.data['Level']}",
            f"| damage = {a.data['PvE'].get('Damage', 0)} {a.data['DamageType']}",
            f"| power cost = {a.data['PvE']['PowerCost']}",
            f"| reuse time = {a.data['ResetTime']}",
            f"| range = {a.data['PvE']['Range']} meters",
        ]
    )

    if "Keywords" in a.data:
        s = add_line(
            s,
            "| keywords = "
            + " ".join(map(lambda s: "{{KWAB|%s}}" % s, a.data["Keywords"])),
        )

    if "RageMultiplier" in a.data["PvE"]:
        s = add_line(s, f"| ragemulti = {a.data['PvE']['RageMultiplier']}")

    if "SpecialInfo" in a.data:
        s = add_line(s, f"| special = {a.data['SpecialInfo']}")

    s = add_line(s, "}}")

    return s


def generate_page(a):
    return "\n".join(
        [
            "__NOTOC__",
            generate_infobox(a),
            "<noinclude>[[Category:Abilities]]</noinclude>",
        ]
    )


def generate_pages():
    pages = {}

    for a in get_all_content(Ability):
        if a.data.get("AttributesThatDeltaPowerCost"):  # player ability
            upgrade_of = a.data.get("UpgradeOf")
            if upgrade_of:
                text = f"#redirect [[{upgrade_of}]]"
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
