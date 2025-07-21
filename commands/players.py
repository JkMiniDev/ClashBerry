import os
import discord
import aiohttp
from supabase import create_client, Client
import json  # Added for max.json

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load max.json using absolute path
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    max_json_path = os.path.join(script_dir, 'max.json')
    with open(max_json_path, 'r') as f:
        max_levels = json.load(f)
except FileNotFoundError:
    print(f"Error: 'max.json' not found at {max_json_path}")
    max_levels = {}
except Exception as e:
    print(f"Error loading max.json: {str(e)}")
    max_levels = {}

class PlayerEmbeds:
    ELIXIR_TROOPS = [
        "Barbarian", "Archer", "Giant", "Goblin", "Wall Breaker", "Balloon", "Wizard",
        "Healer", "Dragon", "P.E.K.K.A", "Baby Dragon", "Miner", "Electro Dragon", "Yeti", "Dragon Rider",
        "Electro Titan", "Root Rider", "Thrower"
    ]
    DARK_TROOPS = [
        "Minion", "Hog Rider", "Valkyrie", "Golem", "Witch", "Lava Hound", "Bowler",
        "Ice Golem", "Headhunter", "Apprentice Warden", "Druid", "Furnace"
    ]
    PETS = [
        "L.A.S.S.I", "Electro Owl", "Mighty Yak", "Unicorn", "Frosty", "Diggy", "Poison Lizard",
        "Phoenix", "Spirit Fox", "Angry Jelly", "Sneezy"
    ]
    ELIXIR_SPELLS = [
        "Lightning Spell", "Healing Spell", "Rage Spell", "Jump Spell", "Freeze Spell", "Clone Spell",
        "Invisibility Spell", "Recall Spell", "Revive Spell"
    ]
    DARK_SPELLS = [
        "Poison Spell", "Earthquake Spell", "Haste Spell", "Skeleton Spell", "Bat Spell",
        "Overgrowth Spell", "Ice Block Spell"
    ]
    SIEGE_MACHINES = [
        "Wall Wrecker", "Battle Blimp", "Stone Slammer", "Siege Barracks", "Log Launcher",
        "Flame Flinger", "Battle Drill", "Troop Launcher"
    ]
    HEROES = [
        "Barbarian King", "Archer Queen", "Grand Warden", "Royal Champion", "Minion Prince"
    ]
    HERO_EQUIPMENT_NAMES = [
        "Giant Gauntlet", "Rocket Spear", "Spiky Ball", "Frozen Arrow", "Fireball",
        "Snake Bracelet", "Dark Crown", "Magic Mirror", "Electro Boots", "Action Figure",
        "Barbarian Puppet", "Rage Vial", "Archer Puppet", "Invisibility Vial", "Eternal Tome",
        "Life Gem", "Seeking Shield", "Royal Gem", "Earthquake Boots", "Hog Rider Puppet",
        "Haste Vial", "Giant Arrow", "Healer Puppet", "Rage Gem", "Healing Tome",
        "Henchmen Puppet", "Dark Orb", "Metal Pants", "Vampstache", "Noble Iron"
    ]

    EMOJI_MAP = {
        "Barbarian": "<:Barbarian:1389335307236675685>", "Archer": "<:Archer:1389335191251845231>",
        "Giant": "<:Giant:1389335532559007814>", "Goblin": "<:Goblin:1389335575005233193>",
        "Wall Breaker": "<:Wall_Breaker:1389335868778479717>", "Balloon": "<:Balloon:1389335241256079380>",
        "Wizard": "<:Wizard:1389335896410685522>", "Healer": "<:Healer:1389335608538959962>",
        "Dragon": "<:Dragon:1389335375628996710>", "P.E.K.K.A": "<:PEKKA:1389335693284610089>",
        "Baby Dragon": "<:Baby_Dragon:1389335213921931475>", "Miner": "<:Miner:1389335649756123246>",
        "Electro Dragon": "<:Electro_Dragon:1389335412635467907>", "Yeti": "<:Yeti:1389335923468140646>",
        "Dragon Rider": "<:Dragon_Rider:1389335344712777810>", "Electro Titan": "<:Electro_Titan:1389335495456067644>",
        "Root Rider": "<:Root_Rider:1389335791104163992>", "Thrower": "<:Thrower:1389335835991605379>",
        "Minion": "<:Minion:1389335067490259105>", "Hog Rider": "<:Hog_Rider:1389334936606998658>",
        "Valkyrie": "<:Valkyrie:1389335108896428113>", "Golem": "<:Golem:1389334870211428442>",
        "Witch": "<:Witch:1389335145458303117>", "Lava Hound": "<:Hound:1389334971927363594>",
        "Bowler": "<:Bowler:1389334752762400879>", "Ice Golem": "<:Ice_Golem:1389335012922490910>",
        "Headhunter": "<:Headhunter:1389334896895463515>", "Apprentice Warden": "<:Apprentice_Warden:1389334711972921446>",
        "Druid": "<:Druid:1389334776518807692>", "Furnace": "<:Furnace:1389334827890770062>",
        "L.A.S.S.I": "<:LASSI:1389487671314878564>", "Electro Owl": "<:Electro_Owl:1389487627102715915>",
        "Mighty Yak": "<:Mighty_Yak:1389487701597753404>", "Unicorn": "<:Unicorn:1389487875770421268>",
        "Frosty": "<:Frosty:1389487647897944135>", "Diggy": "<:Diggy:1389487605615296522>",
        "Poison Lizard": "<:Poison_Lizard:1389487747412267079>", "Phoenix": "<:Phoenix:1389487721075965962>",
        "Spirit Fox": "<:Spirit_Fox:1389487837207859251>", "Angry Jelly": "<:Angry_Jelly:1389487961107861604>",
        "Sneezy": "<:Sneezy:1389487576142057632>",
        "Lightning Spell": "<:Lightning_Spell:1389514690991755425>", "Healing Spell": "<:Healing_Spell:1389514619588182076>",
        "Rage Spell": "<:Rage_Spell:1389514709677510676>", "Jump Spell": "<:Jump_Spell:1389514668518936697>",
        "Freeze Spell": "<:Freeze_Spell:1389514596272046100>", "Clone Spell": "<:Clone_Spell:1389514566077251584>",
        "Invisibility Spell": "<:Invisibility_Spell:1389514646830059670>", "Recall Spell": "<:Recall_Spell:1389514740153319494>",
        "Revive Spell": "<:Revive_Spell:1389514763209539635>", "Poison Spell": "<:Poison_Spell:1389514511496511580>",
        "Earthquake Spell": "<:Earthquake_Spell:1389514428755742730>", "Haste Spell": "<:Haste_Spell:1389514451694391336>",
        "Skeleton Spell": "<:Skeleton_Spell:1389514529594933389>", "Bat Spell": "<:Bat_Spell:1389785143434154135>",
        "Overgrowth Spell": "<:Overgrowth_Spell:1389514490894352415>", "Ice Block Spell": "<:Ice_Block_Spell:1389514470933659709>",
        "Wall Wrecker": "<:Wall_Wrecker:1389488366076035102>", "Battle Blimp": "<:Battle_Blimp:1389488182009266176>",
        "Stone Slammer": "<:Stone_Slammer:1389488329820737537>", "Siege Barracks": "<:Siege_Barracks:1389488293980278884>",
        "Log Launcher": "<:Log_Launcher:1389488260056875110>", "Flame Flinger": "<:Flame_Flinger:1389488228322644058>",
        "Battle Drill": "<:Battle_Drill:1389488196097933383>", "Troop Launcher": "<:Troop_Launcher:1389488137989783683>",
        "Barbarian King": "<:BK:1389336058910478448>", "Archer Queen": "<:AQ:1389336028124287058>",
        "Grand Warden": "<:GW:1389336084990656766>", "Royal Champion": "<:RC:1389336174530789386>",
        "Minion Prince": "<:MP:1389336146106126586>", "Giant Gauntlet": "<:Giant_Gauntlet:1389486373370728569>",
        "Rocket Spear": "<:Rocket_Spear:1389485541812211772>", "Spiky Ball": "<:Spiky_Ball:1389486543609008201>",
        "Frozen Arrow": "<:Frozen_Arrow:1389485830241914921>", "Fireball": "<:Fireball_Equipment:1389481472930615366>",
        "Snake Bracelet": "<:Snake_Bracelet:1389486502324736000>", "Dark Crown": "<:Dark_Crown:1389486099436671128>",
        "Magic Mirror": "<:Magic_Mirror:1389485991529549854>", "Electro Boots": "<:Electro_Boots:1389485474560610316>",
        "Action Figure": "<:Action_Figure:1389485645558448168>", "Barbarian Puppet": "<:Barbarian_Puppet:1389486300289306675>",
        "Rage Vial": "<:Rage_Vial:1389486468249948200>", "Archer Puppet": "<:Archer_Puppet:1389485687467806780>",
        "Invisibility Vial": "<:Invisibility_Vial:1389485950471508059>", "Eternal Tome": "<:Eternal_Tome:1389481544938291343>",
        "Life Gem": "<:Life_Gem:1389481627733852200>", "Seeking Shield": "<:Seeking_Shield:1389485584657027164>",
        "Royal Gem": "<:Royal_Gem:1389485562821480478>", "Earthquake Boots": "<:Earthquake_Boots:1389486333029908521>",
        "Hog Rider Puppet": "<:Hog_Rider_Puppet:1389485508874338426>", "Haste Vial": "<:Haste_Vial:1389485494378827839>",
        "Giant Arrow": "<:Giant_Arrow:1389485842594267248>", "Healer Puppet": "<:Healer_Puppet:1389485904497741824>",
        "Rage Gem": "<:Rage_Gem:1389481664731938877>", "Healing Tome": "<:Healing_Tome:1389481568673726515>",
        "Henchmen Puppet": "<:Henchmen_Puppet:1389486155308863488>", "Dark Orb": "<:Dark_Orb:1389486134156984421>",
        "Metal Pants": "<:Metal_Pants:1389486183435866113>", "Vampstache": "<:Vampstache:1389486580200374302>",
        "Noble Iron": "<:Noble_Iron:1389486200150036481>",
        "TH1": "<:TH1:1389337801044131933>",
        "TH2": "<:TH2:1389338126907998238>",
        "TH3": "<:TH3:1389338161372729556>",
        "TH4": "<:TH4:1389338196155830373>",
        "TH5": "<:TH5:1389338267044020375>",
        "TH6": "<:TH6:1389338294055079956>",
        "TH7": "<:TH7:1389338322639523910>",
        "TH8": "<:TH8:1389338353907929278>",
        "TH9": "<:TH9:1389338445863714826>",
        "TH10": "<:TH10:1389337837756743770>",
        "TH11": "<:TH11:1389337873526030517>",
        "TH12": "<:TH12:1389337901132677202>",
        "TH13": "<:TH13:1389337944837591152>",
        "TH14": "<:TH14:1389337974185136189>",
        "TH15": "<:TH15:1389338002114744362>",
        "TH16": "<:TH16:1389338032766980247>",
        "TH17": "<:TH17:1389338065650319430>"
    }
# Profile Info
    @staticmethod
    def format_number(number):
        """Convert a number to abbreviated format (e.g., 2000 -> 2K, 2200000 -> 2.2M, 1500000000 -> 1.5B)."""
        if number < 1000:
            return str(number)
        elif number < 1000000:
            return f"{number / 1000:.1f}K".rstrip('0').rstrip('.')
        elif number < 1000000000:
            return f"{number / 1000000:.1f}M".rstrip('0').rstrip('.')
        else:
            return f"{number / 1000000000:.1f}B".rstrip('0').rstrip('.')

    @staticmethod
    def player_info(player_data):
        embed = discord.Embed(
            title=f"{player_data.get('name', '?')} ({player_data.get('tag', '?')})",
            color=0xcccccc
        )

        # Description: Town Hall with emoji, Exp, and Trophies in one line
        th_level = player_data.get('townHallLevel', '?')
        exp_level = player_data.get('expLevel', '?')
        trophies = player_data.get('trophies', '?')
        th_emoji = PlayerEmbeds.EMOJI_MAP.get(f"TH{th_level}", f"TH{th_level}")
        try:
            embed.description = f"{th_emoji} {th_level} <:EXP:1390652382693556324> {exp_level} <:Trophy:1390652405649248347> {trophies}"
        except Exception as e:
            print(f"Error setting embed description: {str(e)}")
            embed.description = f"TH{th_level} Exp: {exp_level} Trophies: {trophies}"

        # Clan: Name (clickable link) - Role
        clan = player_data.get("clan", {})
        clan_name = clan.get("name", "None")
        role_raw = player_data.get("role", "notInClan")
        role_map = {
            "admin": "Elder",
            "coLeader": "Co-Leader",
            "leader": "Leader",
            "member": "Member",
            "notInClan": "Not In Clan"
        }
        clan_role = role_map.get(role_raw, "Unknown")
        if clan_name != "None" and clan.get("tag"):
            clan_tag = clan["tag"].replace("#", "")
            clan_url = f"https://link.clashofclans.com/?action=OpenClanProfile&tag=%23{clan_tag}"
            clan_display = f"[{clan_name}]({clan_url})"
            embed.add_field(name="Clan", value=f"{clan_display} - {clan_role}", inline=False)
        else:
            embed.add_field(name="Clan", value="Not In Clan", inline=False)

        # Season Stats
        season_stats = (
            f"<:Arrow_Right:1390721523765088447> Donated: {player_data.get('donations', 0)}\n"
            f"<:Arrow_Left:1390721571508977858> Received: {player_data.get('donationsReceived', 0)}\n"
            f"<:Sword:1390659453321351289> Attack Wins: {player_data.get('attackWins', 0)}\n"
            f"<:Shield:1390659485273423914> Defense Wins: {player_data.get('defenseWins', 0)}"
        )
        embed.add_field(name="Season Stats", value=season_stats, inline=False)

        # New War Stats field
        achievements = {a["name"]: a["value"] for a in player_data.get("achievements", [])}
        war_preference_raw = player_data.get("warPreference")
        war_preference = war_preference_raw.capitalize() if war_preference_raw else ""
        war_lines = [
            f"<:Star_1:1391862120706212041> War Stars: {player_data.get('warStars', '?')}",
            f"<:Star:1390656503987568651> CWL Stars: {achievements.get('War League Legend', 0)}"
        ]
        if war_preference == "In":
            war_lines.append(f"<:Opt_in:1395090219711070370> Preference: In")
        elif war_preference == "Out":
            war_lines.append(f"<:Opt_out:1395090188643860560> Preference: Out")
        war_stats = "\n".join(war_lines)
        embed.add_field(name="War Stats", value=war_stats, inline=False)

        # Overall Stats (remaining achievements)
        overall_stats = (
            f"<:Gold:1390666299054755950> Total Loot: <:Gold:1390666299054755950> {PlayerEmbeds.format_number(achievements.get('Gold Grab', 0))} <:Elixir:1390666277856608306> {PlayerEmbeds.format_number(achievements.get('Elixir Escapade', 0))} <:Dark_Elixir:1390666254670630912> {PlayerEmbeds.format_number(achievements.get('Heroic Heist', 0))}\n"
            f"<:Trophy:1390652405649248347> Best Trophy: {player_data.get('bestTrophies', '?')}\n"
            f"<:Sword:1390659453321351289> Attack Wins: {achievements.get('Conqueror', 0)}\n"
            f"<:Shield:1390659485273423914> Defense Wins: {achievements.get('Unbreakable', 0)}\n"
            f"<:Troops_Donation:1390659367241781279> Troops Donated: {achievements.get('Friend in Need', 0)}\n"
            f"<:Spell_Donation:1390659413613744228> Spells Donated: {achievements.get('Sharing is caring', 0)}\n"
            f"<:Siege_Donation:1390659389786030232> Siege Donated: {achievements.get('Siege Sharer', 0)}\n"
            f"<:Clan_games:1390660765509488774> Clan Games: {achievements.get('Games Champion', 0)}\n"
            f"<:Capital_Gold:1390661279697338420> Capital Looted: {achievements.get('Aggressive Capitalism', 0)}\n"
            f"<:Capital_Gold:1390661279697338420> Capital Donated: {achievements.get('Most Valuable Clanmate', 0)}"
        )
        embed.add_field(name="Overall Stats", value=overall_stats, inline=False)

        # Discord field with Supabase query
        try:
            player_tag = player_data.get("tag", "")
            # Query all records and check if player_tag is in verified or unverified lists
            response = supabase.table("linked_players").select("discord_id, verified, unverified").execute()
            discord_id = "Not Linked"
            verified = False
            if response.data:
                for record in response.data:
                    if player_tag in record.get("verified", []):
                        discord_id = f"<@{record.get('discord_id', 'Not Linked')}>"
                        verified = True
                        break
                    elif player_tag in record.get("unverified", []):
                        discord_id = f"<@{record.get('discord_id', 'Not Linked')}>"
                        verified = False
                        break
            verified_emoji = "<:Verified:1390721846420439051>"  # From /accounts command
            discord_value = f"{discord_id} {verified_emoji}" if verified and discord_id != "Not Linked" else discord_id
        except Exception as e:
            print(f"Error querying Supabase for linked player: {str(e)}")
            discord_value = "Not Linked"

        embed.add_field(name="Discord", value=discord_value, inline=False)

        # League icon (if available)
        icon = player_data.get("league", {}).get("iconUrls", {}).get("medium")
        if icon:
            embed.set_thumbnail(url=icon)
        else:
            embed.set_thumbnail(url="https://i.imghippo.com/files/aYq7201ZC.png")
        return embed

    @staticmethod
    def unit_embed(player_data):
        troops = player_data.get("troops", [])
        spells = player_data.get("spells", [])
        heroes = player_data.get("heroes", [])
        hero_equipment = player_data.get("heroEquipment", [])
        th_level = str(player_data.get("townHallLevel", 1))  # Get TH level, default to 1 if missing

        def format_level(level, max_level):
            """Format level with spaces based on digit count"""
            level_str = str(level)
            max_str = str(max_level)
            # Add space before if level is single digit
            prefix = " " if len(level_str) == 1 else ""
            # Add space after if max is single digit
            suffix = " " if len(max_str) == 1 else ""
            return f"`{prefix}{level_str}/{max_str}{suffix}`"

        def troop_lines(names):
            units = [t for t in troops if t.get("name") in names and max_levels.get(t.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(t.get('name'), '❓')} {format_level(t['level'], max_levels.get(t.get('name'), {}).get(th_level, 0))}"
                        for t in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def spell_lines(names):
            units = [s for s in spells if s.get("name") in names and max_levels.get(s.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(s.get('name'), '❓')} {format_level(s['level'], max_levels.get(s.get('name'), {}).get(th_level, 0))}"
                        for s in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def pet_lines():
            units = [t for t in troops if t.get("name") in PlayerEmbeds.PETS and max_levels.get(t.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(t.get('name'), '❓')} {format_level(t['level'], max_levels.get(t.get('name'), {}).get(th_level, 0))}"
                        for t in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def siege_lines():
            units = [t for t in troops if t.get("name") in PlayerEmbeds.SIEGE_MACHINES and max_levels.get(t.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(t.get('name'), '❓')} {format_level(t['level'], max_levels.get(t.get('name'), {}).get(th_level, 0))}"
                        for t in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def hero_lines():
            units = [h for h in heroes if h.get("name") in PlayerEmbeds.HEROES and max_levels.get(h.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(h.get('name'), '❓')} {format_level(h['level'], max_levels.get(h.get('name'), {}).get(th_level, 0))}"
                        for h in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def equipment_lines():
            units = [eq for eq in hero_equipment if eq.get("name") in PlayerEmbeds.HERO_EQUIPMENT_NAMES and max_levels.get(eq.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(eq.get('name'), '❓')} {format_level(eq.get('level', '?'), max_levels.get(eq.get('name'), {}).get(th_level, 0))}"
                        for eq in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result if result else ["None"]

        embed = discord.Embed(
            title="Army Overview",
            color=0xcccccc
        )
        elixir_troops_value = troop_lines(PlayerEmbeds.ELIXIR_TROOPS)
        if elixir_troops_value[0] != "None":
            embed.add_field(name="Elixir Troops", value=elixir_troops_value[0], inline=False)
            for extra_value in elixir_troops_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        dark_troops_value = troop_lines(PlayerEmbeds.DARK_TROOPS)
        if dark_troops_value[0] != "None":
            embed.add_field(name="Dark Troops", value=dark_troops_value[0], inline=False)
            for extra_value in dark_troops_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        elixir_spells_value = spell_lines(PlayerEmbeds.ELIXIR_SPELLS)
        if elixir_spells_value[0] != "None":
            embed.add_field(name="Elixir Spells", value=elixir_spells_value[0], inline=False)
            for extra_value in elixir_spells_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        dark_spells_value = spell_lines(PlayerEmbeds.DARK_SPELLS)
        if dark_spells_value[0] != "None":
            embed.add_field(name="Dark Spells", value=dark_spells_value[0], inline=False)
            for extra_value in dark_spells_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        siege_machines_value = siege_lines()
        if siege_machines_value[0] != "None":
            embed.add_field(name="Siege Machines", value=siege_machines_value[0], inline=False)
            for extra_value in siege_machines_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        heroes_value = hero_lines()
        if heroes_value[0] != "None":
            embed.add_field(name="Heroes", value=heroes_value[0], inline=False)
            for extra_value in heroes_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        pets_value = pet_lines()
        if pets_value[0] != "None":
            embed.add_field(name="Pets", value=pets_value[0], inline=False)
            for extra_value in pets_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        equipment_value = equipment_lines()
        if equipment_value[0] != "None":
            embed.add_field(name="Hero Equipment", value=equipment_value[0], inline=False)
            for extra_value in equipment_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        return embed

class ViewSelector(discord.ui.Select):
    def __init__(self, player_data, current_view):
        self.player_data = player_data
        options = [
            discord.SelectOption(
                label="Profile Overview",
                description="Show player profile information",
                emoji="<:EXP:1390652382693556324>",
                default=(current_view == "Profile Overview")
            ),
            discord.SelectOption(
                label="Army Overview",
                description="Show troops, spells, and heroes",
                emoji="<:Troops:1395132747043049544>",
                default=(current_view == "Army Overview")
            )
        ]
        super().__init__(
            placeholder="Select a view...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Profile Overview":
            embed = PlayerEmbeds.player_info(self.player_data)
        else:
            embed = PlayerEmbeds.unit_embed(self.player_data)
        
        view = ProfileButtonView(self.player_data, current_view=self.values[0])
        await interaction.response.edit_message(embed=embed, view=view)

class ProfileButtonView(discord.ui.View):
    def __init__(self, player_data, current_view="Profile Overview"):
        super().__init__(timeout=None)
        self.player_data = player_data
        self.player_tag = player_data.get("tag", "")
        self.current_view = current_view

        self.add_item(ViewSelector(player_data, current_view))

        self.refresh_btn = discord.ui.Button(
            emoji="🔃",
            style=discord.ButtonStyle.secondary,
            custom_id="refresh_btn"
        )
        self.refresh_btn.callback = self.refresh_btn_callback
        self.add_item(self.refresh_btn)

        if self.player_tag:
            tag = self.player_tag.replace("#", "")
            url = f"https://link.clashofclans.com/?action=OpenPlayerProfile&tag=%23{tag}"
            self.add_item(discord.ui.Button(
                label="Open In-game",
                url=url,
                style=discord.ButtonStyle.link
            ))

    async def refresh_btn_callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        fresh_data = await get_coc_player(self.player_tag)
        if not fresh_data:
            await interaction.followup.send("⚠️ Interaction expired. Please run the command again.", ephemeral=True)
            return
        
        new_view = ProfileButtonView(fresh_data, current_view=self.current_view)
        if self.current_view == "Profile Overview":
            embed = PlayerEmbeds.player_info(fresh_data)
        else:
            embed = PlayerEmbeds.unit_embed(fresh_data)
        
        await interaction.followup.edit_message(interaction.message.id, embed=embed, view=new_view)

async def get_coc_player(player_tag):
    url = f"https://cocproxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            print(f"get_coc_player failed with status: {resp.status}")
            return None

async def get_linked_players(discord_id):
    try:
        response = supabase.table("linked_players").select("*").eq("discord_id", discord_id).execute()
        if response.data:
            user_data = response.data[0]
            accounts = []
            for tag in user_data.get("verified", []) + user_data.get("unverified", []):
                player_data = await get_coc_player(tag)
                player_name = player_data.get("name", tag) if player_data else tag
                accounts.append({"name": player_name, "tag": tag})
            return accounts
        return []
    except Exception as e:
        print(f"Supabase get_linked_players error: {e}")
        return []

def setup(bot):
    async def player_tag_autocomplete(interaction: discord.Interaction, current: str):
        accounts = await get_linked_players(str(interaction.user.id))
        return [
            discord.app_commands.Choice(
                name=f"{acc['name']} ({acc['tag']})",
                value=acc['tag']
            )
            for acc in accounts
            if current.lower() in acc['tag'].lower() or current.lower() in acc['name'].lower()
        ][:25]

    @bot.tree.command(name="player", description="Get player information")
    @discord.app_commands.describe(tag="Player tag (e.g. #2Q82LRL)")
    @discord.app_commands.autocomplete(tag=player_tag_autocomplete)
    async def player_command(interaction: discord.Interaction, tag: str):
        await interaction.response.defer()
        player_data = await get_coc_player(tag)
        if not player_data:
            await interaction.followup.send("No account found for the provided tag.", ephemeral=True)
            return

        view = ProfileButtonView(player_data, current_view="Profile Overview")
        embed = PlayerEmbeds.player_info(player_data)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)