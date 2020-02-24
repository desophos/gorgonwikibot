from functools import lru_cache

from userscripts.GorgonWiki import cdn


class Content:
    def __init__(self, id, data):
        self.id = id
        self.data = data


class Item(Content):
    def __init__(self, id, data):
        super().__init__(id, data)
        self.name = data["Name"]


class Recipe(Content):
    def __init__(self, id, data):
        super().__init__(id, data)
        self.name = data["Name"]


class Quest(Content):
    def __init__(self, id, data):
        super().__init__(id, data)
        self.name = data["Name"]

        area, npcid = data["FavorNPC"].split("/")
        try:
            self.npc = get_content_by_id("npcs", npcid)
        except KeyError:
            name = npcid
            # Hack for scripted event NPCs not present in the JSON
            for event in ("LiveNpc_", "NPC_Halloween_"):
                if event in name:
                    name = name.replace(event, "").replace("_", " ")
                    break
            self.npc = Npc(npcid, {"Name": name, "AreaName": area})


class Npc(Content):
    def __init__(self, id, data):
        super().__init__(id, data)
        self.name = data["Name"]
        self.ref = data["AreaName"] + "/" + self.name


class Area(Content):
    """Allows to alias an area if the wiki uses a different name than the data files"""

    def __init__(self, id, data):
        super().__init__(id, data)
        self.name = data["FriendlyName"]
        self.short_name = data.get("ShortFriendlyName", self.name)

    def get_alias(self):
        if self.id == "AreaRahuCaves":
            return "Rahu Sewer"
        elif self.id in ("AreaCasino", "AreaKurCaves"):
            return self.name
        else:
            return self.short_name

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
