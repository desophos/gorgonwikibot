import sys

from scripts.create_ai_profiles import get_abilities, is_valid_ability


def write_template(abilities, key, filename):
    with open(filename, "w") as f:
        f.writelines(f"| {k}={v[key]}\n" for k, v in abilities)


if __name__ == "__main__":
    abilities = get_abilities(is_valid_ability).items()
    write_template(abilities, "Description", "logs/abilities.txt")
    write_template(abilities, "IconID", "logs/icons.txt")
