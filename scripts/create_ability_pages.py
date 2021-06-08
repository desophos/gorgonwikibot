import re
import sys
from operator import attrgetter

import pywikibot
from gorgonwikibot.content import (
    Ability,
    Skill,
    get_all_content,
    get_content_by_id,
    get_content_by_iname,
    get_name_from_iname,
    separate_words,
)
from gorgonwikibot.entrypoint import entrypoint

# Front Kick is in Unarmed and Cow
duplicates = ["Front Kick"]  # disambiguation between skills
disambiguate = {
    name: f"{name} (ability)"
    for name in ["First Aid", "Rabbit's Foot", "Lycanspore Bomb"]
}  # disambiguation from another page with same name


def pluralize(n, unit):
    return f"{n} {unit}{'' if n == 1 else 's'}"


def maybe_join(xs, sep=" "):
    return sep.join(filter(None, xs))


def s_if_in(s, x, xs):
    v = xs.get(x, "")
    return s.format(v) if v else v


def is_learnable(a):
    keywords = a.data.get("Keywords")
    return "Lint_NotLearnable" not in keywords if keywords else True


def ability_chains():
    # assume no base ability has a number in its name
    # can't use just letters because of apostrophes & colons
    # Call Stabled Pet has "#"
    regex = re.compile(r"(?: ?[^\d\s#]+)+")
    chains = {}
    for a in get_all_content(Ability):
        if (
            (
                a.data.get("AttributesThatDeltaPowerCost")
                or a.data.get("AttributesThatModPowerCost")
            )
            and is_learnable(a)
            and a.iname != "FaeBombSporeTrigger"  # not a learnable ability
            and a.iname != "CharmRat"  # this page has descriptive info
            or a.iname in ["Punch", "SwordSlash"]  # you start with these abilities
        ):  # learnable player ability
            basename = re.search(regex, a.name)[0]
            basename = disambiguate.get(basename, basename)
            if basename in duplicates:
                basename += f" ({separate_words(a.data['Skill'])})"
            try:
                chains[basename].append(a)
            except KeyError:
                chains[basename] = [a]

    # we can use alphabetical sorting as long as
    # ability upgrades are just called "Base Name 2" etc.
    # this also groups variants together, e.g. Claw Barrage
    return {k: sorted(v, key=attrgetter("name")) for k, v in chains.items()}


def process_keywords(a):
    keywords = a.data.get("Keywords", "")
    return (
        "| keywords = " + "".join("{{KWAB|%s}}" % s for s in keywords)
        if keywords
        else ""
    )


def process_ragemulti(a):
    multi = a.data["PvE"].get("RageMultiplier", "")
    return f"| ragemulti = {multi}" if multi != "" else ""


def process_specialvalues(a):
    def format_val(v):
        return maybe_join([v["Label"], str(v["Value"]), v["Suffix"]]) + "."

    values = a.data["PvE"].get("SpecialValues", "")
    return " ".join(format_val(v) for v in values) if values else ""


def process_specialinfo(a):
    info = a.data.get("SpecialInfo", "")
    return info + ("." if info and not info.endswith(".") else "")


def process_dots(a):
    # Assume that no ability has multiple DoT effects.
    # A maximum of one damaging effect and one special effect are handled.
    dots, special = "", ""

    if "DoTs" in a.data["PvE"]:
        for dot in a.data["PvE"]["DoTs"]:
            if "SpecialRules" in dot and "BuffActivated" in dot["SpecialRules"]:
                pass
            elif "Preface" in dot:
                special = " ".join(
                    [
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

    return dots, special


def process_damage(a):
    damage = ""

    dots, special = process_dots(a)

    # get whichever damage is there; only one is present
    damage_amt = a.data["PvE"].get(
        "Damage",
        a.data["PvE"].get(
            "HealthSpecificDamage", a.data["PvE"].get("ArmorSpecificDamage", 0)
        ),
    )
    if damage_amt:
        damage = maybe_join(
            [
                str(damage_amt),
                a.data["DamageType"],
                s_if_in("to health", "HealthSpecificDamage", a.data["PvE"]),
                s_if_in("to armor", "ArmorSpecificDamage", a.data["PvE"]),
                s_if_in(
                    "+ {} if target is Vulnerable",
                    "ExtraDamageIfTargetVulnerable",
                    a.data["PvE"],
                ),
            ]
        )

    if dots:
        damage = f"{damage} initially and {dots}" if damage_amt else dots

    return damage, special


def generate_infobox(a):
    s = [
        "{{Ability infobox",
        f"| name = {a.name}",
        f"| description = {a.data['Description']}",
        f"| level = {a.data['Level']}",
        f"| power cost = {a.data['PvE']['PowerCost']}",
        f"| reuse time = {a.data['ResetTime']}",
        f"| range = {a.data['PvE']['Range']} meters",
    ]
    specials = []

    try:
        skill = get_content_by_id(Skill, a.data["Skill"]).name
    except KeyError:
        skill = "Unknown"
    s.append(f"| skill = {skill}")

    s.append(process_keywords(a))
    s.append(process_ragemulti(a))

    specials.append(process_specialvalues(a))
    specials.append(process_specialinfo(a))

    damage, dmg_special = process_damage(a)
    if damage:
        s.append(f"| damage = {damage}")
    specials.append(dmg_special)

    special = maybe_join(specials)
    if special:
        s.append(f"| special = {special}")

    s.append("}}")

    return maybe_join(s, "\n")


def generate_infoboxes(chain):
    if len(chain) == 1:
        return generate_infobox(chain[0])
    else:
        return "\n".join(
            [
                "{| width=100%",
                "\n".join("\n".join(["|-", "|", generate_infobox(a)]) for a in chain),
                "|}",
            ]
        )


def generate_page(chain):
    return "\n".join(
        [
            "__NOTOC__",
            generate_infoboxes(chain),
            "<noinclude>[[Category:Abilities]]</noinclude>",
        ]
    )


def generate_pages():
    pages = {}
    disambiguation = {
        "First Aid (ability)": "You may be looking for the Skill '''[[First Aid]]'''.",
    }
    disambiguation.update(
        (name, f"You may be looking for the creature '''[[{name} (mob)|{name}]]'''.")
        for name in ["Cold Sphere", "Acid Sigil", "Electricity Sigil"]
    )

    def add_disambiguation_box(title):
        return "\n".join(
            [
                "{{ambox",
                f"| type = {disambiguation[title]}",
                "| border = yellow",
                "}}",
                pages[title],
            ]
        )

    for basename, chain in ability_chains().items():
        pages[basename] = generate_page(chain)
        for a in chain:
            # redirect duplicates to disambiguation page
            # for duplicates, firstname should equal pre-modification basename
            firstname = chain[0].name
            realbasename = firstname if firstname in duplicates else basename
            # create redirect pages for any non-basename abilities
            # this includes those where the basename ability doesn't exist:
            # Flare Fireball and Raise Skeletal Ratkin Mage
            if (
                disambiguate.get(a.name, a.name) != realbasename
            ):  # already created base page
                pages[a.name] = f"#redirect [[{realbasename}]]"

    for title in disambiguation:
        pages[title] = add_disambiguation_box(title)

    # sanitize page titles
    # looking at you Call Stabled Pet #1-6
    pages = {title.replace("#", ""): page for title, page in pages.items()}

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
def main(site, options):
    for title, text in generate_pages().items():
        page = pywikibot.Page(site, title)
        if page.text == text:
            pywikibot.output(f"No changes to {title}")
            continue
        page.text = text
        if options.dry:
            pywikibot.output(f"\n{title}\n{page.text}\n")
        else:
            page.save(summary=options.msg or "Create ability page")


if __name__ == "__main__":
    main(sys.argv)


"""potentially useful functions that ended up being unnecessary

def count_prereqs(a):
    req = a.data.get("Prerequisite")
    if not req:
        return 0
    else:
        return 1 + count_prereqs(get_content_by_iname(Ability, req))

def prereq_sort(a, b):
    # sanity checks
    assert a.iname != b.iname, f"{a.iname} and {b.iname} are the same ability!"
    assert a.data.get("UpgradeOf") == b.data.get(
        "UpgradeOf"
    ), f"{a.iname} and {b.iname} aren't UpgradeOf the same ability!"

    areq = a.data.get("Prerequisite")
    breq = b.data.get("Prerequisite")

    # one is a base ability
    if not areq:
        return a
    elif not breq:
        return b
    # one has the other as Prerequisite
    elif breq == a.iname:
        return a
    elif areq == b.iname:
        return b
    # one has more prerequisites than the other
    elif count_prereqs(b) > count_prereqs(a):
        return a
    elif count_prereqs(a) > count_prereqs(b):
        return b
    else:
        raise NotImplementedError(f"unable to sort {a.iname} vs. {b.iname}")
"""
