# Project: Gorgon Wiki Bot
Collaboration and contributions are welcome! Please feel free to reach out if you're interested in using this bot in your own project.

## Usage
1. Installing gorgonwikibot
    * [Install poetry](https://python-poetry.org/docs/#installation).
    * Clone gorgonwikibot locally.
    * Run `poetry install` in your cloned repository.
2. Filling in your user config files
    * Insert your Gorgon Wiki username into your local copy of `user-config.py` where the placeholder is.
    * Follow the instructions in `user-password.py` to insert your own login information into your local copy of `user-password.py`.
    * Your changes to these files should stay on your local machine. Don't git commit them!
3. Congratulations, your installation is complete!
    * You can now run scripts, e.g. `poetry run python scripts/create_ability_pages.py`.

## Script arguments
* `--dry` Dry-run mode prints page source instead of modifying the wiki.
* `--msg` Use a custom edit message for the wiki.
* `--quest "name"` Run the script only for a specific quest (by "Name").
* `--offset n` Skip the first n quests in the data file.
