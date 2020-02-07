from create_ai_profiles import get_abilities
from GorgonWiki.RemoteData import Cdn


def write_template(abilities, key, filename):
    with open(filename, "w") as f:
        f.writelines(f"| {k}={v[key]}\n" for k, v in abilities)


def main():
    abilities = get_abilities(Cdn()).items()
    write_template(abilities, "Description", "abilities.txt")
    write_template(abilities, "IconID", "icons.txt")


if __name__ == "__main__":
    main()
