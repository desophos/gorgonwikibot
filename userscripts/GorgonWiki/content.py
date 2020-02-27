import re
from functools import lru_cache

from userscripts.GorgonWiki import cdn


class Content:
    def __init__(self, id, data):
        self.id = id
        self.data = data
        self.name = data.get("Name")  # for convenience


class Item(Content):
    def __init__(self, id, data):
        super().__init__(id, data)


class Recipe(Content):
    def __init__(self, id, data):
        super().__init__(id, data)


class Quest(Content):
    def __init__(self, id, data):
        super().__init__(id, data)

        area, npcid = data["FavorNPC"].split("/")
        try:
            self.npc = get_content_by_id("npcs", npcid)
        except KeyError:
            # Hack for scripted event NPCs not present in npcs.json
            name = npcid
            for event in ("LiveNpc_", "NPC_Halloween_"):
                name = separate_words(name.replace(event, ""))
                break
            self.npc = Npc(npcid, {"Name": name, "AreaName": area})


class Npc(Content):
    def __init__(self, id, data):
        super().__init__(id, data)
        self.ref = data["AreaName"] + "/" + self.name


class Area(Content):
    """Allows to alias an area if the wiki uses a different name than the data files"""

    def __init__(self, id, data):
        super().__init__(id, data)
        self._name = data["FriendlyName"]

    @property
    def name(self):
        if self.id == "AreaRahuCaves":
            return "Rahu Sewer"
        elif self.id in ("AreaCasino", "AreaKurCaves"):
            return self._name
        else:
            return self.data.get("ShortFriendlyName", self._name)

    def get_prefix(self):
        if self.id in ("AreaCasino", "AreaDesert1", "AreaKurMountains", "AreaKurCaves"):
            return "the "
        else:
            return ""


file2cls = {
    "areas": Area,
    "npcs": Npc,
    "items": Item,
    "recipes": Recipe,
    "quests": Quest,
}


def separate_words(name):
    return re.sub(r"(.)([A-Z])", r"\1 \2", name)


@lru_cache
def get_content_by_id(which, id):
    data = cdn.get_file(which)
    return file2cls[which](id, data[id])


@lru_cache
def get_content_by_match(which, matchkey, matchval):
    data = cdn.get_file(which)
    for k, v in data.items():
        if v[matchkey] == matchval:
            return file2cls[which](k, v)
