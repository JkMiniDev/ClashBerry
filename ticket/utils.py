import os
import json
import aiohttp
import base64
from urllib.parse import urlparse, parse_qs
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import disnake

load_dotenv()

COC_API_TOKEN = os.getenv("API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Initialize MongoDB client only if database name is set
if MONGODB_DATABASE:
    mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    db = mongodb_client[MONGODB_DATABASE]
else:
    print("Warning: MONGODB_DATABASE environment variable is not set")
    mongodb_client = None
    db = None

# Load max_lvl.json using absolute path
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    max_json_path = os.path.join(script_dir, 'config', 'max_lvl.json')
    with open(max_json_path, 'r') as f:
        max_levels = json.load(f)
except FileNotFoundError:
    print(f"Error: 'max_lvl.json' not found at {max_json_path}")
    max_levels = {}
except Exception as e:
    print(f"Error loading max_lvl.json: {str(e)}")
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

    # Load emoji mappings from JSON files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(script_dir, 'emoji', 'town_halls.json'), 'r') as f:
            TH_EMOJIS = json.load(f)
        with open(os.path.join(script_dir, 'emoji', 'home_units.json'), 'r') as f:
            UNIT_EMOJIS = json.load(f)
        
        # Combine all emojis into one map for compatibility
        EMOJI_MAP = {**UNIT_EMOJIS}
        for th_level, emoji in TH_EMOJIS.items():
            EMOJI_MAP[f"TH{th_level}"] = emoji
    except Exception as e:
        print(f"Error loading emoji files: {e}")
        EMOJI_MAP = {}

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
        player_tag = player_data.get('tag', '')
        player_name = player_data.get('name', '?')
        
        # Create clickable title URL
        title_url = None
        if player_tag and player_tag.startswith('#'):
            tag_clean = player_tag[1:]
            title_url = f"https://link.clashofclans.com/?action=OpenPlayerProfile&tag=%23{tag_clean}"
        
        embed = disnake.Embed(
            title=f"{player_name} ({player_tag})",
            url=title_url,
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

        # War Stats field
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

        # Discord field - will be set by the calling function
        discord_value = player_data.get("discord_info", "Not Linked")
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

        embed = disnake.Embed(
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

class TicketViewSelector(disnake.ui.Select):
    def __init__(self, player_data, current_view):
        self.player_data = player_data
        options = [
            disnake.SelectOption(
                label="Profile Overview",
                description="Show player profile information",
                emoji="<:EXP:1390652382693556324>",
                default=(current_view == "Profile Overview")
            ),
            disnake.SelectOption(
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

    async def callback(self, interaction: disnake.Interaction):
        if self.values[0] == "Profile Overview":
            embed = PlayerEmbeds.player_info(self.player_data)
        else:
            embed = PlayerEmbeds.unit_embed(self.player_data)
        
        view = TicketProfileView(self.player_data, current_view=self.values[0])
        await interaction.response.edit_message(embed=embed, view=view)

class TicketProfileView(disnake.ui.View):
    def __init__(self, player_data, current_view="Profile Overview"):
        super().__init__(timeout=None)
        self.player_data = player_data
        self.player_tag = player_data.get("tag", "")
        self.current_view = current_view

        self.add_item(TicketViewSelector(player_data, current_view))

async def get_guild_data(guild_id, panel_name=None):
    """Get guild data from MongoDB, optionally filter by panel name"""
    if db is None:
        print("Error: MongoDB not initialized. Check environment variables.")
        return None
    
    try:
        guild_settings_collection = db.guild_settings
        query = {"guild_id": str(guild_id)}
        if panel_name:
            query["panel_name"] = panel_name
        
        result = await guild_settings_collection.find_one(query)
        if result:
            print(f"get_guild_data: Found data for guild_id={guild_id}, panel_name={panel_name}: {result}")
            return result
        print(f"get_guild_data: No data found for guild_id={guild_id}, panel_name={panel_name}")
        return None
    except Exception as e:
        print(f"Error fetching guild data for guild_id={guild_id}, panel_name={panel_name}: {e}")
        return None

async def get_panel_names(guild_id):
    """Get list of panel names for a guild (for autocomplete)"""
    if db is None:
        print("Error: MongoDB not initialized. Check environment variables.")
        return []
    
    try:
        guild_settings_collection = db.guild_settings
        cursor = guild_settings_collection.find({"guild_id": str(guild_id)})
        panel_names = []
        async for document in cursor:
            if "panel_name" in document:
                panel_names.append(document["panel_name"])
        print(f"get_panel_names: Found panel names for guild_id={guild_id}: {panel_names}")
        return panel_names
    except Exception as e:
        print(f"Error fetching panel names for guild_id={guild_id}: {e}")
        return []

async def save_guild_data(guild_id, panel_name, staff_role_id=None, category_id=None, panel_embed_data=None, welcome_embed_data=None, button_label=None, button_color=None):
    """Save guild and panel data to MongoDB"""
    if db is None:
        print("Error: MongoDB not initialized. Check environment variables.")
        return
    
    try:
        guild_settings_collection = db.guild_settings
        data = {
            "guild_id": str(guild_id),
            "panel_name": panel_name,
            "staff_role_id": staff_role_id,
            "category_id": category_id,
            "panel_embed_data": panel_embed_data,
            "welcome_embed_data": welcome_embed_data,
            "button_label": button_label,
            "button_color": button_color
        }
        print(f"save_guild_data: Saving data for guild_id={guild_id}, panel_name={panel_name}: {data}")

        # Use upsert to update existing or insert new record
        await guild_settings_collection.replace_one(
            {"guild_id": str(guild_id), "panel_name": panel_name}, 
            data, 
            upsert=True
        )
        print(f"save_guild_data: Saved record for guild_id={guild_id}, panel_name={panel_name}")
    except Exception as e:
        print(f"Error saving guild data for guild_id={guild_id}: {e}")

async def get_staff_role(guild, panel_name=None):
    """Get staff role from guild data, optionally filter by panel name"""
    guild_data = await get_guild_data(guild.id, panel_name)
    if guild_data and guild_data.get("staff_role_id"):
        role = guild.get_role(int(guild_data["staff_role_id"]))
        if role:
            print(f"get_staff_role: Found staff role {role.name} (ID: {guild_data['staff_role_id']}) for guild_id={guild.id}, panel_name={panel_name}")
            return role
        else:
            print(f"get_staff_role: Role ID {guild_data['staff_role_id']} not found in guild_id={guild.id}")
    else:
        print(f"get_staff_role: No staff_role_id found for guild_id={guild.id}, panel_name={panel_name}")
    return None

async def get_category_id(guild, panel_name=None):
    """Get category ID from guild data, optionally filter by panel name"""
    guild_data = await get_guild_data(guild.id, panel_name)
    if guild_data:
        category_id = guild_data.get("category_id")
        print(f"get_category_id: Found category_id={category_id} for guild_id={guild.id}, panel_name={panel_name}")
        return category_id
    print(f"get_category_id: No category_id found for guild_id={guild.id}, panel_name={panel_name}")
    return None

async def get_welcome_embed_data(guild_id, panel_name=None):
    """Get welcome embed data from MongoDB"""
    guild_data = await get_guild_data(guild_id, panel_name)
    if guild_data:
        print(f"get_welcome_embed_data: Found welcome embed data for guild_id={guild_id}, panel_name={panel_name}")
        return guild_data.get("welcome_embed_data")
    print(f"get_welcome_embed_data: No welcome embed data for guild_id={guild_id}, panel_name={panel_name}")
    return None

async def get_panel_embed_data(guild_id, panel_name):
    """Get panel embed data from MongoDB"""
    guild_data = await get_guild_data(guild_id, panel_name)
    if guild_data:
        print(f"get_panel_embed_data: Found panel embed data for guild_id={guild_id}, panel_name={panel_name}")
        return guild_data.get("panel_embed_data")
    print(f"get_panel_embed_data: No panel embed data for guild_id={guild_id}, panel_name={panel_name}")
    return None

async def get_button_data(guild_id, panel_name):
    """Get button label and color from MongoDB"""
    guild_data = await get_guild_data(guild_id, panel_name)
    if guild_data:
        print(f"get_button_data: Found button data for guild_id={guild_id}, panel_name={panel_name}: label={guild_data.get('button_label')}, color={guild_data.get('button_color')}")
        return guild_data.get("button_label"), guild_data.get("button_color")
    print(f"get_button_data: No button data for guild_id={guild_id}, panel_name={panel_name}")
    return None, None

async def delete_guild_data(guild_id, panel_name=None):
    """Delete guild or panel data from MongoDB"""
    if db is None:
        print("Error: MongoDB not initialized. Check environment variables.")
        return False
    
    try:
        guild_settings_collection = db.guild_settings
        query = {"guild_id": str(guild_id)}
        if panel_name:
            query["panel_name"] = panel_name
        
        result = await guild_settings_collection.delete_many(query)
        print(f"delete_guild_data: Deleted {result.deleted_count} document(s) for guild_id={guild_id}, panel_name={panel_name}")
        return True
    except Exception as e:
        print(f"Error deleting guild data for guild_id={guild_id}, panel_name={panel_name}: {e}")
        return False

async def parse_discohook_link(link):
    """Parse Discohook link and return embed data"""
    try:
        parsed = urlparse(link)
        query = parse_qs(parsed.query)

        # Case 1: ?share=ID
        if "share" in query:
            share_id = query["share"][0]
            url = f"https://discohook.app/api/v1/share/{share_id}"
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; DiscordBot/1.0)"
            }
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        print(f"parse_discohook_link: Failed to fetch share link {url}, status={resp.status}")
                        return None
                    data = await resp.json()
            data = data.get("data", {}).get("messages", [{}])[0].get("data", {})
            content = data.get("content", None)
            embeds = data.get("embeds", [])

        # Case 2: ?data=base64
        elif "data" in query:
            base64_data = query["data"][0]
            base64_data = base64_data + "=" * ((4 - len(base64_data) % 4) % 4)
            decoded = base64.b64decode(base64_data).decode("utf-8")
            raw_data = json.loads(decoded)
            data = raw_data.get("messages", [{}])[0].get("data", {})
            content = data.get("content", None)
            embeds = data.get("embeds", [])

        else:
            print(f"parse_discohook_link: Invalid Discohook link format: {link}")
            return None

        print(f"parse_discohook_link: Successfully parsed link {link}")
        return {
            "content": content,
            "embeds": embeds
        }

    except Exception as e:
        print(f"Error parsing Discohook link {link}: {e}")
        return None

async def get_coc_player(player_tag):
    """Fetch Clash of Clans player data"""
    url = f"https://cocproxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                print(f"get_coc_player: Successfully fetched player data for tag {player_tag}")
                return await resp.json()
            else:
                print(f"get_coc_player: Failed to fetch player data for tag {player_tag}, status={resp.status}")
                return None

async def show_profile(interaction, player_data):
    """Display enhanced Clash of Clans player profile with dropdown menu"""
    embed = PlayerEmbeds.player_info(player_data)
    view = TicketProfileView(player_data)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)