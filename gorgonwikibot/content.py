import re
from functools import lru_cache

from gorgonwikibot import cdn


class Content:
    def __init__(self, id, data):
        self.id = id
        self.data = data
        self.errors = []
        self.notices = []

    @property
    def name(self):
        return self.data.get("Name")

    @property
    def iname(self):
        return self.data.get("InternalName")

    @property
    def link(self):
        return f"[[{self.name}]]"


class Item(Content):
    datafile = "items"

    def __init__(self, id, data):
        super().__init__(id, data)

    @property
    def link(self):
        return "{{Item|%s}}" % self.name


class Recipe(Content):
    datafile = "recipes"

    def __init__(self, id, data):
        super().__init__(id, data)


class Skill(Content):
    datafile = "skills"

    def __init__(self, id, data):
        super().__init__(id, data)
        # name doesn't change, so figure it out now
        self._name = self.data.get("Name") or self.id

    @property
    def name(self):
        return self._name


class Ability(Content):
    datafile = "abilities"

    def __init__(self, id, data):
        super().__init__(id, data)

    @property
    def link(self):
        skill = self.data.get("Skill")
        if skill and skill != "Unknown":
            return f"[[{skill}|{self.name}]]"
        else:
            return f"[[{self.name}]]"


class Npc(Content):
    datafile = "npcs"

    def __init__(self, id, data):
        super().__init__(id, data)
        self.ref = data["AreaName"] + "/" + self.name


class Area(Content):
    """Allows to alias an area if the wiki uses a different name than the data files"""

    datafile = "areas"

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

    @property
    def prefix(self):
        if self.id in ("AreaCasino", "AreaDesert1", "AreaKurMountains", "AreaKurCaves"):
            return "the "
        else:
            return ""


def separate_words(name):
    """Convenience function for inserting spaces into CamelCase names."""
    return re.sub(r"(.)([A-Z])", r"\1 \2", name)


@lru_cache
def get_all_content(cls):
    return [cls(id, data) for id, data in cdn.get_file(cls.datafile).items()]


@lru_cache
def get_content_by_id(cls, id):
    data = cdn.get_file(cls.datafile)
    return cls(id, data[id])


@lru_cache
def get_content_by_match(cls, matchkey, matchval):
    data = cdn.get_file(cls.datafile)
    for k, v in data.items():
        if v[matchkey] == matchval:
            return cls(k, v)


def get_content_by_iname(cls, iname):
    """Convenience wrapper for searching by InternalName."""
    return get_content_by_match(cls, "InternalName", iname)


def get_name_from_iname(cls, iname):
    """Convenience wrapper for finding the Name corresponding to an InternalName."""
    return get_content_by_iname(cls, iname).name
