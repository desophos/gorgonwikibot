
class Quest:
    def __init__(self, name):
        self.name = name
        self.errors = []
        self.notices = []
        self.summary = ""
        self.summary_extra = ""
        self.prereq = ""
        self.preface = ""
        self.midway_text = ""
        self.objectives = ""
        self.rewards = ""
        self.success = ""

from userscripts.GorgonWiki.content import (Content, Item, Npc, Recipe, Skill,
                                            get_content_by_id,
                                            get_content_by_match,
                                            separate_words)

        try:
            npc = NpcList.find_npc_by_ref(data["FavorNpc"])
        except KeyError:
            self.errors.append("NPC not found")
            npc = Npc(data["FavorNpc"], AreaList.find_by_areaname(data["DisplayedLocation"]))
        area = npc.area
        area_alias = area.get_alias()
        area_prefix = area.get_prefix()
        if "DisplayedLocation" in data:
            # Some areas have a good display location, some don't. Overwrite when we know it is nice.
            if data["DisplayedLocation"] == "Sacred Grotto":
                area_alias = data["DisplayedLocation"]
                area_prefix = "the "

    def requirements_text(self):
        events = {
            "LiveEvent_Crafting": "a Crafting Caravan event",
            "Event_Christmas": "Christmas",
            "LiveEvent_CivilService": "a Civil Service event",
            "LiveEvent_BunFu": "a Bun-Fu event",
        }

        restrictions = {
            "IsWarden": "for Wardens",
            "AreaEventOn": "during an event in the area",  # check req["AreaEvent"]
            "HangOutCompleted": "after completing a hangout",  # check req["HangOut"]
            "InteractionFlagSet": "after an interaction",  # check req["InteractionFlag"]
            "IsLongtimeAnimal": "to long time animals",
        }

        def helper(reqdata):
            reqs = []
            for req in reqdata:
                reqtype = req["T"]

                if reqtype == "Or":
                    reqs.extend(helper(req["List"]))
                elif reqtype == "MinFavorLevel":
                    reqs.append(
                        "The quest is available at {{Favor|%s}} favor."
                        % separate_words(req["Level"])
                    )
                elif reqtype == "MinSkillLevel":
                    reqs.append(
                        "This quest is available at %s level %s."
                        % (get_content_by_id(Skill, req["Skill"]).link, req["Level"])
                    )
                elif reqtype in ("QuestCompleted", "GuildQuestCompleted"):
                    reqs.append(
                        "You must have previously completed %s in order to undertake this quest."
                        % get_content_by_match(Quest, "InternalName", req["Quest"]).link
                    )
                elif reqtype == "HasEffectKeyword" and "Keyword" in req:
                    try:
                        reqs.append(
                            f"This quest is only available during {events[req['Keyword']]}."
                        )
                    except KeyError as e:
                        self.errors.append(f"Unknown event: {e}")
                else:
                    try:
                        reqs.append(
                            f"This quest is only available {restrictions[reqtype]}."
                        )
                    except KeyError as e:
                        self.errors.append(f"Unknown requirement: {e}")
                return reqs

        return " ".join(helper(self.data["Requirements"]))

    def wiki_source(self):
        currencies = {"WardenPoints": "Warden Points", "Gold": "councils"}
        source = {}
        objectives = []
        rewards = []

        def reuse_time(num, timespan):
            return "This quest can be repeated after {} {}{}.".format(
                num, timespan, "" if num == 1 else "s"
            )

        def bullet_list(items):
            return map(lambda s: f"* {s}\n", items)

        def linebreak_source(key, suffix="\n\n"):
            return source[key] + suffix if key in source else ""

        for k, v in self.data.items():
            if k in ("InternalName", "IsCancellable", "Name", "Version"):
                pass  # Tech stuff
            elif k in ("FavorNpc", "DisplayedLocation"):
                pass  # NPC is handled above
            elif k == "TSysLevel":
                pass  # Not sure what that is. I don't think we should display it.
            elif k == "GroupingName":
                pass  # Tech value to group quests so you can only have one of the group. Like casino daily.
            elif k in (
                "IsGuildQuest",
                "NumExpectedParticipants",
                "IsAutoWrapUp",
                "IsAutoPreface",
                "ReuseTime_Minutes",
            ):
                pass  # Guild quest stuff
            elif k == "Keywords":
                pass  # This might be interesting, but only used for guild quests atm?
            elif k == "RequirementsToSustain":
                pass  # Probably used to auto-cancel quests after events like halloween
            elif k in ("PreGiveItems", "PreGiveRecipes"):
                pass
            elif k == "Description":
                source[k] = f"==Summary==\n{v.strip()}"
            elif k == "MidwayText":
                source[k] = f"===Midway===\n{v.strip()}"
            elif k == "ReuseTime_Days":
                source["ReuseTime"] = reuse_time(v, "day")
            elif k == "ReuseTime_Hours":
                source["ReuseTime"] = reuse_time(v, "hour")
            elif k == "Requirements":
                source[k] = self.requirements_text()
            elif k == "PrefaceText":
                source[k] = f"===Preface===\n{v.strip()}"
            elif k == "Objectives":
                for obj in self.data["Objectives"]:
                    desc = obj["Description"]
                    if obj["Type"] == "Collect" and "ItemName" in obj:
                        item = get_content_by_match(
                            Item, "InternalName", obj["ItemName"]
                        )
                        desc = desc.replace(item.name, item.link)

                    try:
                        n = obj["Number"]
                    except KeyError:
                        pass
                    else:
                        if n > 1 and desc.find(str(n)) == -1:
                            desc += f" x{n}"

                    objectives.append(desc)
            elif k == "SuccessText":
                source[k] = "{{Quote|%s}}" % v
            elif k == "Reward_Favor":
                rewards.append(f"{v} [[Favor]]")
            elif k == "Reward_Gold":
                rewards.append(f"{v} councils")
            elif k == "Rewards_Currency":
                for curr, amt in v.items():
                    try:
                        rewards.append(f"{amt} {currencies[curr]}")
                    except KeyError as e:
                        self.errors.append(f"Unknown reward currency: {e}")
            elif k == "Rewards_Items":
                for item in v:
                    reward = get_content_by_match(
                        Item, "InternalName", item["Item"]
                    ).link
                    if item["StackSize"] > 1:
                        reward += f" x{item['StackSize']}"
                    rewards.append(reward)
            elif k == "Rewards":
                # Rewards is a list, maybe sometimes a dict?
                for reward in v:
                    if reward["T"] in ("SkillXP", "SkillXp"):  # Inconsistent uppercase
                        rewards.append(
                            "%i XP in %s"
                            % (
                                reward["Xp"],
                                get_content_by_id(Skill, reward["Skill"]).link,
                            )
                        )
                    elif reward["T"] == "Recipe":
                        rewards.append(
                            "Recipe: %s"
                            % get_content_by_match(
                                Recipe, "InternalName", reward["Recipe"]
                            ).link
                        )
                    elif reward["T"] == "GuildXp":
                        rewards.append(f"{reward['Xp']} Guild XP")
                    elif reward["T"] == "GuildCredits":
                        rewards.append(f"{reward['Credits']} Guild Credits")
                    else:
                        self.errors.append(f"Unexpected reward type: {reward['T']}")
            elif k == "Rewards_Effects":
                self.notices.append(
                    f"Special reward effects must be handled manually: {v}"
                )
            elif k == "Rewards_NamedLootProfile":
                rewards.append("random items")  # Special loot table for rewards
            else:
                self.errors.append(f"Unhandled key: {k}")

    def get_errors(self):
        return self.errors

    def get_notices(self):
        return self.notices


class Favor:
    @staticmethod
    def get_alias(name):
        return re.sub(r'(.)([A-Z])', r'\1 \2', name)


class Skill:
    @staticmethod
    def get_alias(name):
        return re.sub(r'(.)([A-Z])', r'\1 \2', name)

        area = get_content_by_id("areas", self.npc.data["AreaName"])
        if "DisplayedLocation" in self.data:
            # Some areas have a good display location, some don't. Overwrite when we know it is nice.
            if self.data["DisplayedLocation"] == "Sacred Grotto":
                area.name = self.data["DisplayedLocation"]
                area.prefix = "the "

        return "".join(
            "__NOTOC__\n",
            source["Description"],
            "\n\n",
            linebreak_source("ReuseTime"),
            "===Prerequisites===\n",
            "To start this quest, talk to '''%s''' in %s'''%s'''. "
            % (self.npc.link, area.prefix, area.link),
            linebreak_source("Requirements"),
            linebreak_source("PrefaceText"),
            linebreak_source("MidwayText"),
            "===Requirements===\n",
            bullet_list(objectives),
            "===Rewards===\n",
            "{{Spoiler|Rewards|\n",
            linebreak_source("SuccessText", "\n"),
            bullet_list(rewards),
            "}}\n\n",
            "[[Category:Quests]]",
            "[[Category:Quests/%s Quests]]" % area.name,
            "[[Category:Quests/%s]]" % self.npc.name,
            "\n",
        )
