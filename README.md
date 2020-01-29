# GorgonWikibot
Bot scripts for the Project: Gorgon Wiki

## Usage
* Install pywikibot
* Link userscripts/ to <pywikibot>/scripts/userscripts/ (or copy the files there)
* Link projectgorgon_family.py to <pywikibot>/pywikibot/families/
* Configure pywikibot (user detail)
* Run pywikibot, e.g. "python pwb.py create_missing_quest_pages"

## Script detail
### create_missing_quest_pages
* ```-dry-run``` Print the page source instead of saving to the wiki
* ```-quest:"name"``` Only work for the quest with this name
* ```-offset:n``` Skip n quests from the beginning
