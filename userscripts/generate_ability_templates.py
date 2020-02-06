from create_ai_profiles import get_abilities


def write_template(filename, key):
    with open(filename, "w") as f:
        f.writelines(f"| {k}={v[key]}\n" for k, v in get_abilities().items())


def main():
    write_template("abilities.txt", "desc")
    write_template("icons.txt", "icon")


if __name__ == "__main__":
    main()
