import argparse

import pywikibot


def entrypoint(main):
    parser = argparse.ArgumentParser(
        description="Entrypoint for scripts dealing with the Project: Gorgon wiki."
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        help="dry-run mode prints page source instead of modifying the wiki",
    )
    parser.add_argument(
        "--quest", help='run the script only for a specific quest (by "Name")'
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="skip the first n quests in the data file",
    )

    def wrapper(argv):
        local_args = pywikibot.handle_args(argv[1:])
        options = parser.parse_args(local_args)

        site = pywikibot.Site()
        site.login()
        user = site.user()
        if user:
            pywikibot.output(f"Logged in on {site} as {user}.")
        else:
            pywikibot.output(f"Not logged in on {site}.")

        if options.dry:
            pywikibot.output("Dry-run mode, not creating pages...\n")

        main(options)

    return wrapper
