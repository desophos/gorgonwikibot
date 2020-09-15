# GorgonWikibot
Bot scripts for the Project: Gorgon Wiki

## Usage
1. Installing GorgonWikibot
    * [Install poetry](https://python-poetry.org/docs/#installation)
    * Clone GorgonWikibot locally
    * `cd` to GorgonWikibot directory and `poetry install`
2. Generating pywikibot user files
    * [Download pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/Installation#Install_Pywikibot)
    * `cd` to pywikibot directory and `python pwb.py generate_user_files.py`
    * Copy the produced `user-password.py` into the GorgonWikibot directory.
    * Insert your username into this repository's `user-config.py`.
3. Congratulations, your installation is complete!
    * You can now run scripts, e.g. `poetry run python scripts/create_quest_pages.py`

## Script arguments
* `--dry` Print the page source instead of saving to the wiki
* `--quest "name"` Only work for the quest with this name
* `--offset n` Skip n quests from the beginning
