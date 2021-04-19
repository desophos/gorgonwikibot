import sys

from scripts.create_ai_profiles import get_abilities


def write_template(abilities, key, filename):
    with open(filename, "w") as f:
        f.writelines(f"| {k}={v[key]}\n" for k, v in abilities.items())


if __name__ == "__main__":

    def validator(a):
        return not a.is_player

    abilities = {}
    for k, v in get_abilities(validator).items():
        if not v["Description"]:
            v["Description"] = "(No Description)"
        abilities[k] = v

    write_template(abilities, "Description", "logs/abilities.txt")
    write_template(abilities, "IconID", "logs/icons.txt")
