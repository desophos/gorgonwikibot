import pywikibot
from pywikibot.bot import (
    SingleSiteBot, ExistingPageBot, NoRedirectPageBot, AutomaticTWSummaryBot)

# debug stuff
#from pprint import pprint
import time

from scripts.userscripts.GorgonWiki import RemoteData, WikiTools


def get_wiki_template(name):
    q = WikiTools.Quest(name.strip())
    #print("*** Wiki template for quest " + name + "\n")
    source = q.generate_wiki_source()
    notices = q.get_notices()
    if notices:
        pywikibot.output("#################################### NOTICE:\n" + "\n".join(notices))
    errors = q.get_errors()
    if errors:
        print("\n\nERRORS:")
        print("\n".join(errors))
        raise RuntimeError("Something is not right, see console output")
    return source


def main(*args):
    # Handle params
    local_args = pywikibot.handle_args(args)
    dry_run = False
    quest_filter = None
    offset = 0

    for arg in local_args:
        option, sep, value = arg.partition(':')
        if option == "-dry-run":
            dry_run = True
        if option == "-quest":
            quest_filter = value
        if option == "-offset":
            offset = int(value)

    # Get quest list
    if quest_filter:
        quest_list = {"filtered": RemoteData.QuestList.find_quest_by_name(quest_filter)}
    else:
        quest_list = RemoteData.QuestList.get_all()
    quest_blacklist = ["quest_1", "quest_2"]

    # Connect to API
    site = pywikibot.Site()
    current_offset = 0

    for index in quest_list:
        current_offset += 1
        if current_offset < offset:
            continue  # Can I skip the first items of a dict smarter?

        if index in quest_blacklist:
            continue

        quest = quest_list[index]

        if "Keywords" in quest:
            # Skip work orders
            if "WorkOrder" in quest["Keywords"]:
                #pywikibot.output("Skipping work order quest")
                continue
        if not "FavorNpc" in quest:
            pywikibot.output("Skipping quest without FavorNpc: {}".format(quest["Name"]))
            continue
        if quest["FavorNpc"] == "":
            pywikibot.output("Skipping quest with empty FavorNpc: {}".format(quest["Name"]))
            continue

        pywikibot.output('Loading %s...' % quest["Name"])
        page = pywikibot.Page(site, quest["Name"])
        if not page.exists():
            pywikibot.output("Missing page for quest {}".format(quest["Name"]))
            pywikibot.output("Current offset is {}".format(current_offset))

            page.text = get_wiki_template(quest["Name"])
            if dry_run:
                pywikibot.output("Dry-run mode")
                pywikibot.output(page.text + "\n\n")
            else:
                page.save(summary="Create quest page")
                pywikibot.output("Page saved for quest {}".format(quest["Name"]))


if __name__ == "__main__":
    main()