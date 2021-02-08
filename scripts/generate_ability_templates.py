import sys

from scripts.create_ai_profiles import get_abilities


def write_template(abilities, key, filename):
    with open(filename, "w") as f:
        f.writelines(f"| {k}={v[key]}\n" for k, v in abilities)


if __name__ == "__main__":

    def validator(a):
        return not a.is_player and a.data["Description"]

    abilities = get_abilities(validator).items()
    write_template(abilities, "Description", "logs/abilities.txt")
    write_template(abilities, "IconID", "logs/icons.txt")
