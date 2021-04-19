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

    @property
    def iname(self):
        return self.id


class Ability(Content):
    from enum import Enum

    datafile = "abilities"
    PetCommands = Enum("Command", "BASIC SIC TRICK")

    def __init__(self, id, data):
        super().__init__(id, data)

    @property
    def link(self):
        skill = self.data.get("Skill")
        if skill and skill != "Unknown":
            return f"[[{skill}|{self.name}]]"
        else:
            return f"[[{self.name}]]"

    @property
    def is_player(self):
        return any(
            s in self.data
            for s in ("AttributesThatDeltaPowerCost", "AttributesThatModPowerCost")
        )

    @property
    def is_pet(self):
        return (
            "Pet" in self.iname
            and not self.is_player
            and self.iname
            not in ("PetUndeadArrow1", "PetUndeadArrow2", "PetUndeadOmegaArrow")
        )  # SkeletonDistanceArcher

    @property
    def which_pet_command(self):
        kw = self.data.get("Keywords")
        if kw:
            if "PetBasicAttack" in kw:
                return Ability.PetCommands.BASIC
            elif "PetA" in kw:
                return Ability.PetCommands.SIC
            elif "PetB" in kw:
                return Ability.PetCommands.TRICK
        raise ValueError(f"{self.name} is not a pet command")

    @property
    def is_player_minigolem(self):
        return (
            "Minigolem" in self.iname
            and "Enemy" not in self.iname
            and self.iname
            not in (
                "MinigolemBombToss4",
                "MinigolemPunch4",
                "MinigolemRageAcidToss4",
            )  # SecurityGolem
        )

    @property
    def is_enemy(self):
        return not any([self.is_player, self.is_pet, self.is_player_minigolem])


class Ai(Content):
    datafile = "ai"

    def __init__(self, id, data):
        super().__init__(id, data)

    @property
    def name(self):
        return self.id

    @property
    def iname(self):
        return self.id

    @property
    def is_pet(self):
        return "_Pet" in self.iname

    @property
    def is_player_minigolem(self):
        return "Minigolem" in self.iname and "Enemy" not in self.iname

    @property
    def is_enemy(self):
        return not any([self.is_pet, self.is_player_minigolem])

    def abilities(self, include_scaled=False):
        def is_scaled(name, params):
            # some abilities have duplicates scaled to higher levels
            return (
                "minLevel" in params
                and params["minLevel"] > 1  # SnailRage and SpiderKill
                and re.search(r"[B-Z2-9]$", name)
            )

        return [
            name
            for name, params in self.data["Abilities"].items()
            if include_scaled or not is_scaled(name, params)
        ]


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
