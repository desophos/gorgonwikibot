from userscripts.GorgonWiki.content import (Content, Item, Npc, Recipe, Skill,
                                            get_content_by_id,
                                            get_content_by_match,
                                            separate_words)


class Quest(Content):
    datafile = "quests"

    def __init__(self, id, data):
        super().__init__(id, data)

        # Occasionally, quests with a single requirement use a dict instead of a one-item list.
        # Make it always a list for consistency and ease of processing.
        if "Requirements" in self.data and not isinstance(
            self.data["Requirements"], list
        ):
            self.data["Requirements"] = [self.data["Requirements"]]

        if self.data.get("FavorNpc"):
            area, npcid = self.data["FavorNpc"].split("/")
            try:
                self.npc = get_content_by_id(Npc, npcid)
            except KeyError:
                # Hack for scripted event NPCs not present in npcs.json
                self.notices.append(
                    "FavorNpc not found in npcs.json. Generating replacement."
                )
                name = npcid
                for event in ("LiveNpc_", "NPC_Halloween_"):
                    name = separate_words(name.replace(event, ""))
                    break
                self.npc = Npc(npcid, {"Name": name, "AreaName": area})
        else:
            self.npc = None

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

        requirements = self.data["Requirements"]
        if isinstance(requirements[0], list):
            # in a few christmas quests, for no apparent reason,
            # Requirements has an extra nested list
            requirements = requirements[0]

        return " ".join(helper(requirements))

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
            return "".join(map(lambda s: f"* {s}\n", items))

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
            elif k in ("PreGiveItems", "PreGiveRecipes", "PreGiveEffects"):
                pass
            elif k == "Description":
                source[k] = f"==Summary==\n{v.strip()}"
            elif k == "MidwayText":
                if v:  # Fiery Secrets has empty MidwayText
                    source[k] = f"===Midway===\n{v.strip()}"
            elif k == "MidwayGiveItems":
                source[k] = "[%s]" % " ".join(
                    "You receive %s."
                    % get_content_by_match(Item, "InternalName", item["Item"]).link
                    for item in v
                )
            elif k == "ReuseTime_Days":
                source["ReuseTime"] = reuse_time(v, "day")
            elif k == "ReuseTime_Hours":
                source["ReuseTime"] = reuse_time(v, "hour")
            elif k == "Requirements":
                source[k] = self.requirements_text()
            elif k == "PrerequisiteFavorLevel":
                # Only the Fiery Secrets quests have this
                # keep line lengths short
                text = "This quest is available at {{Favor|%s}} favor."
                source[k] = text % separate_words(v)
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
            elif k in ("Reward_Favor", "Rewards_Favor"):
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
            elif k == "Rewards_XP":
                for name, xp in v.items():
                    rewards.append(
                        "%i XP in %s" % (xp, get_content_by_id(Skill, name).link)
                    )
            elif k == "Rewards_Ability":
                rewards.append(
                    "Ability: %s"
                    % get_content_by_match(Ability, "InternalName", v).link
                )
            elif k == "Rewards":
                for reward in v:
                    if reward["T"] in ("SkillXP", "SkillXp"):  # Inconsistent uppercase
                        rewards.append(
                            "%i XP in %s"
                            % (
                                reward["Xp"],
                                get_content_by_id(Skill, reward["Skill"]).link,
                            )
                        )
                    elif reward["T"] == "CombatXp":
                        rewards.append(f"{reward['Xp']} XP in active combat skills")
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

        area = get_content_by_id("areas", self.npc.data["AreaName"])
        source["Requirements"] = " ".join(
            (source.get("PrerequisiteFavorLevel", ""), source.get("Requirements", ""))
        ).strip()
        if "DisplayedLocation" in self.data:
            # Some areas have a good display location, some don't. Overwrite when we know it is nice.
            if self.data["DisplayedLocation"] == "Sacred Grotto":
                area.name = self.data["DisplayedLocation"]
                area.prefix = "the "

        return "".join(
            (
                "__NOTOC__\n",
                source["Description"],
                "\n\n",
                linebreak_source("ReuseTime"),
                "===Prerequisites===\n",
                "To start this quest, talk to '''%s''' in %s'''%s'''. "
                % (self.npc.link, areaprefix, arealink),
                linebreak_source("Requirements"),
                linebreak_source("PrefaceText"),
                linebreak_source("MidwayText"),
                linebreak_source("MidwayGiveItems"),
                "===Requirements===\n",
                bullet_list(objectives),
                "\n===Rewards===\n",
                "{{Spoiler|Rewards|\n",
                linebreak_source("SuccessText", "\n"),
                bullet_list(rewards),
                "}}\n\n",
                "[[Category:Quests]]",
                "[[Category:Quests/%s Quests]]" % areaname,
                "[[Category:Quests/%s]]" % self.npc.name,
                "\n",
            )
        )
