import requests
import json
import os
import re


class Cdn:
    """Automatic download of json files, latest version, with local cache"""
    version = None

    def __init__(self):
        self.version = requests.get('http://client.projectgorgon.com/fileversion.txt').text

    def download(self, file):
        r = requests.get('http://cdn.projectgorgon.com/v%s/data/%s.json' % (self.version, file))
        return r.json()

    def get_file(self, file):
        path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '.cache',
            'v' + self.version)
        )
        os.makedirs(path, exist_ok=True)
        filename = os.path.join(path, file + '.json')

        try:
            f = open(filename, 'r')
            data = json.load(f)
            f.close()
            return data
        except FileNotFoundError:
            contents = self.download(file)
            f = open(filename, 'w')
            json.dump(contents, f)
            f.close()
            return contents


class NpcList:
    @staticmethod
    def find_npc_by_ref(ref):
        npc_list = Cdn().get_file("npcs")
        try:
            key = ref.split("/")[-1]
            npc = npc_list[key]
            name = npc["Name"]
            area = npc["AreaName"]
        except KeyError:
            area, name = ref.split("/")
            if name.startswith("LiveNpc_"): # Hack for scripted event npc
                name = name[8:].replace("_", " ")
        return Npc(name, AreaList.find_by_areaname(area))


class AreaList:
    @staticmethod
    def find_by_areaname(name):
        area_list = Cdn().get_file("areas")
        return Area(name, area_list[name])


class Npc:
    def __init__(self, name, area):
        self.name = name
        self.area = area
        self.area_name = area.name
        self.friendly_area_name = area.get_alias()
        self.ref = self.area_name + "/" + self.name

    def get_name(self):
        if self.name.startswith("NPC_Halloween_"):
            return re.sub(r'(.)([A-Z])', r'\1 \2', self.name[14:])
        elif self.name.startswith("NPC_"):
            return re.sub(r'(.)([A-Z])', r'\1 \2', self.name[4:])
        return self.name


class RecipeList:
    @staticmethod
    def find_by_name(name):
        recipe_list = Cdn().get_file("recipes")
        for key in recipe_list:
            if recipe_list[key]["InternalName"] == name:
                return Recipe(recipe_list[key])


class Area:
    """Allows to alias an area if the wiki uses a different name than the data files"""
    def __init__(self, id, data):
        self.id = id
        self.name = data["FriendlyName"]
        self.short_name = data["ShortFriendlyName"] if "ShortFriendlyName" in data else self.name

    def get_alias(self):
        if self.name == "Rahu Sewers":
            return "Rahu Sewer"
        if self.id == "AreaCasino":
            return self.name
        if self.id == "AreaKurCaves":
            return self.name
        return self.short_name

    def get_prefix(self):
        if self.id == "AreaCasino" or self.id == "AreaDesert1" or self.id == "AreaKurMountains" or self.id == "AreaKurCaves":
            return "the "
        return ""


class Item:
    @staticmethod
    def get_name_for_internal(internal):
        item_list = Cdn().get_file("items")
        for key in item_list:
            if item_list[key]["InternalName"] == internal:
                return item_list[key]["Name"]
        return internal


class Recipe:
    def __init__(self, data):
        self.name = data["Name"]


class QuestList:
    @staticmethod
    def find_quest_by_name(name):
        quests = QuestList.get_all()
        for key in quests:
            data = quests[key]
            if data["Name"] == name:
                return data

    @staticmethod
    def find_quest_by_internalname(name):
        quests = QuestList.get_all()
        for key in quests:
            data = quests[key]
            if data["InternalName"] == name:
                return data

    @staticmethod
    def get_all():
        quests = Cdn().get_file("quests")
        return quests