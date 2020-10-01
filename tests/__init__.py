from gorgonwikibot.content import Ability


def dummy_ability(custom=None):
    data = {"Name": "_", "InternalName": "_", "Description": "_"}
    data.update(custom or {})
    return Ability("_", data)
