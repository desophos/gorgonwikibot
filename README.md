# GorgonWikibot
Collaboration and contributions are welcome! Please feel free to reach out if you're interested in using this bot in your own project.

## Usage
1. Installing GorgonWikibot
    * [Install poetry](https://python-poetry.org/docs/#installation)
    * Clone GorgonWikibot locally
    * `cd` to GorgonWikibot directory and `poetry install`
2. Generating pywikibot user files
    * [Download pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation#Install_Pywikibot)
    * `cd` to pywikibot directory and `python pwb.py generate_user_files.py`
    * Copy the produced `user-password.py` into the GorgonWikibot directory
    * Insert your username into this repository's `user-config.py`
    * Optional: Delete pywikibot if desired, since it's only needed to generate your `user-password.py`
3. Congratulations, your installation is complete!
    * You can now run scripts, e.g. `poetry run python scripts/create_ability_pages.py`

## Script arguments
* `--dry` Dry-run mode prints page source instead of modifying the wiki.
* `--msg` Use a custom edit message for the wiki.
* `--quest "name"` Run the script only for a specific quest (by "Name").
* `--offset n` Skip the first n quests in the data file.
