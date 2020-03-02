import sys

import pywikibot
from gorgonwikibot.content import get_all_content, get_content_by_match
from gorgonwikibot.entrypoint import entrypoint
from gorgonwikibot.quest import Quest


@entrypoint
def main(options):
    # Get quest list
    if options.quest:
        quests = [get_content_by_match(Quest, "Name", options.quest)]
    else:
        quests = get_all_content(Quest)

    quest_blacklist = ["KillSkeletons", "VisitGravestones"]

    # Connect to API
    site = pywikibot.Site()
    offset = options.offset

    for quest in quests[offset:]:
        offset += 1

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
        source = quest.wiki_source()

        if page.text == source:
            pywikibot.output(f"No changes to {quest.name}\n")
            continue

        if not page.exists():
            pywikibot.output(f"Missing page for quest {quest.name}")

        pywikibot.output(f"Current offset is {offset}")

        page.text = source

        if quest.notices:
            pywikibot.output(
                "##################### NOTICE:\n" + "\n".join(quest.notices)
            )
        if quest.errors:
            pywikibot.output("\n\nERRORS:\n" + "\n".join(quest.errors))
            raise RuntimeError("Something is not right, see console output")

        if options.dry:
            pywikibot.output(page.text + "\n\n")
        else:
            page.save(summary="Create quest page")
            pywikibot.output(f"Page saved for quest {quest.name}")


if __name__ == "__main__":
    main(sys.argv)
