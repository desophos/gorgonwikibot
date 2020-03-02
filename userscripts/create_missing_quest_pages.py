import pywikibot
from userscripts.GorgonWiki.content import (get_all_content,
                                            get_content_by_match)
from userscripts.GorgonWiki.quest import Quest


def main(*args):
    # Handle params
    local_args = pywikibot.handle_args(args)
    dry_run = False
    quest_filter = None
    offset = 0

    for arg in local_args:
        option, sep, value = arg.partition(":")
        if option == "-dry-run":
            dry_run = True
        if option == "-quest":
            quest_filter = value
        if option == "-offset":
            offset = int(value)

    # Get quest list
    if quest_filter:
        quests = [get_content_by_match(Quest, "Name", quest_filter)]
    else:
        quests = get_all_content(Quest)

    quest_blacklist = ["KillSkeletons", "VisitGravestones"]

    # Connect to API
    site = pywikibot.Site()
    current_offset = 0

    for quest in quests[offset:]:
        current_offset += 1

        if quest.data["InternalName"] in quest_blacklist:
            continue

        if "Keywords" in quest.data and "WorkOrder" in quest.data["Keywords"]:
            # Skip work orders
            # pywikibot.output("Skipping work order quest")
            continue
        if "FavorNpc" not in quest.data:
            pywikibot.output(f"Skipping quest without FavorNpc: {quest.name}")
            continue
        if quest.data["FavorNpc"] == "":
            pywikibot.output(f"Skipping quest with empty FavorNpc: {quest.name}")
            continue

        pywikibot.output(f"Loading {quest.name}...")
        page = pywikibot.Page(site, quest.name)

        if True:  # not page.exists():
            pywikibot.output(f"Missing page for quest {quest.name}")
            pywikibot.output(f"Current offset is {current_offset}")

            page.text = quest.wiki_source()

            if quest.notices:
                pywikibot.output(
                    "##################### NOTICE:\n" + "\n".join(quest.notices)
                )
            if quest.errors:
                pywikibot.output("\n\nERRORS:\n" + "\n".join(quest.errors))
                raise RuntimeError("Something is not right, see console output")

            if dry_run:
                pywikibot.output("Dry-run mode")
                pywikibot.output(page.text + "\n\n")
            else:
                page.save(summary="Create quest page")
                pywikibot.output(f"Page saved for quest {quest.name}")


if __name__ == "__main__":
    main()
