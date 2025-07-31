import os
import json
import aiohttp
import base64
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import discord

load_dotenv()

COC_API_TOKEN = os.getenv("API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Initialize MongoDB client for linked accounts
if MONGODB_DATABASE:
    from motor.motor_asyncio import AsyncIOMotorClient
    mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    accounts_db = mongodb_client[MONGODB_DATABASE]
else:
    print("Warning: MONGODB_DATABASE environment variable is not set")
    mongodb_client = None
    accounts_db = None

# Load ticket configuration from JSON file
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ticket_config.json')
ticket_config = None

def load_config():
    global ticket_config
    try:
        with open(config_path, 'r') as f:
            ticket_config = json.load(f)
        print(f"Ticket configuration loaded successfully from {config_path}")
    except FileNotFoundError:
        print(f"Warning: ticket_config.json not found at {config_path}")
        ticket_config = {}
    except Exception as e:
        print(f"Error loading ticket_config.json: {str(e)}")
        ticket_config = {}

def get_config():
    global ticket_config
    if ticket_config is None:
        load_config()
    return ticket_config

# Load configuration on import
load_config()

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
        
        embed = discord.Embed(
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

class TicketViewSelector(discord.ui.Select):
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
        
        # Check if parent view has selected_accounts (multi-account view)
        if hasattr(self.view, 'selected_accounts') and self.view.selected_accounts:
            view = TicketProfileViewWithSwitcher(self.player_data, self.view.selected_accounts, current_view=self.values[0])
        else:
            view = TicketProfileView(self.player_data, current_view=self.values[0])
        
        await interaction.response.edit_message(embed=embed, view=view)

class TicketProfileView(discord.ui.View):
    def __init__(self, player_data, current_view="Profile Overview"):
        super().__init__(timeout=None)
        self.player_data = player_data
        self.player_tag = player_data.get("tag", "")
        self.current_view = current_view

        self.add_item(TicketViewSelector(player_data, current_view))

def get_staff_role(guild):
    """Get staff role from JSON configuration"""
    config = get_config()
    if config and config.get("staff_role_id"):
        role = guild.get_role(int(config["staff_role_id"]))
        if role:
            print(f"get_staff_role: Found staff role {role.name} (ID: {config['staff_role_id']}) for guild_id={guild.id}")
            return role
        else:
            print(f"get_staff_role: Role ID {config['staff_role_id']} not found in guild_id={guild.id}")
    else:
        print(f"get_staff_role: No staff_role_id found in configuration")
    return None

def get_category_id():
    """Get category ID from JSON configuration"""
    config = get_config()
    if config:
        category_id = config.get("ticket_category_id")
        if category_id:
            print(f"get_category_id: Found category_id={category_id}")
            return int(category_id)
    print(f"get_category_id: No ticket_category_id found in configuration")
    return None

def get_welcome_embed_data():
    """Get welcome embed data from JSON configuration"""
    config = get_config()
    if config and config.get("welcome_embed"):
        print(f"get_welcome_embed_data: Found welcome embed data")
        return config["welcome_embed"]
    print(f"get_welcome_embed_data: No welcome embed data found in configuration")
    return None

def get_panel_embed_data():
    """Get panel embed data from JSON configuration"""
    config = get_config()
    if config and config.get("panel_embed"):
        print(f"get_panel_embed_data: Found panel embed data")
        return config["panel_embed"]
    print(f"get_panel_embed_data: No panel embed data found in configuration")
    return None

def get_button_data():
    """Get button label and color from JSON configuration"""
    config = get_config()
    if config:
        button_label = config.get("button_label", "🎟️ Create Ticket")
        button_color = config.get("button_color", "primary")
        print(f"get_button_data: Found button data: label={button_label}, color={button_color}")
        return button_label, button_color
    print(f"get_button_data: No button data found in configuration, using defaults")
    return "🎟️ Create Ticket", "primary"

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

async def show_profile(interaction, player_data, selected_accounts=None):
    """Display enhanced Clash of Clans player profile with dropdown menu"""
    # Add Discord user info to player data
    player_data_with_discord = player_data.copy()
    player_data_with_discord["discord_info"] = f"<@{interaction.user.id}>"
    
    embed = PlayerEmbeds.player_info(player_data_with_discord)
    
    # If multiple selected accounts, add account switcher to the profile view
    if selected_accounts and len(selected_accounts) > 1:
        view = TicketProfileViewWithSwitcher(player_data_with_discord, selected_accounts)
    else:
        view = TicketProfileView(player_data_with_discord)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

def get_staff_role(guild):
    """Get staff role from JSON configuration"""
    config = get_config()
    if config and config.get("staff_role_id"):
        role = guild.get_role(int(config["staff_role_id"]))
        if role:
            print(f"get_staff_role: Found staff role {role.name} (ID: {config['staff_role_id']}) for guild_id={guild.id}")
            return role
        else:
            print(f"get_staff_role: Role ID {config['staff_role_id']} not found in guild_id={guild.id}")
    else:
        print(f"get_staff_role: No staff_role_id found in configuration")
    return None

def get_category_id():
    """Get category ID from JSON configuration"""
    config = get_config()
    if config:
        category_id = config.get("ticket_category_id")
        if category_id:
            print(f"get_category_id: Found category_id={category_id}")
            return int(category_id)
    print(f"get_category_id: No ticket_category_id found in configuration")
    return None

def get_welcome_embed_data():
    """Get welcome embed data from JSON configuration"""
    config = get_config()
    if config and config.get("welcome_embed"):
        print(f"get_welcome_embed_data: Found welcome embed data")
        return config["welcome_embed"]
    print(f"get_welcome_embed_data: No welcome embed data found in configuration")
    return None

def get_panel_embed_data():
    """Get panel embed data from JSON configuration"""
    config = get_config()
    if config and config.get("panel_embed"):
        print(f"get_panel_embed_data: Found panel embed data")
        return config["panel_embed"]
    print(f"get_panel_embed_data: No panel embed data found in configuration")
    return None

def get_button_data():
    """Get button label and color from JSON configuration"""
    config = get_config()
    if config:
        button_label = config.get("button_label", "🎟️ Create Ticket")
        button_color = config.get("button_color", "primary")
        print(f"get_button_data: Found button data: label={button_label}, color={button_color}")
        return button_label, button_color
    print(f"get_button_data: No button data found in configuration, using defaults")
    return "🎟️ Create Ticket", "primary"
def get_staff_role(guild):
    """Get staff role from JSON configuration"""
    config = get_config()
    if config and config.get("staff_role_id"):
        role = guild.get_role(int(config["staff_role_id"]))
        if role:
            print(f"get_staff_role: Found staff role {role.name} (ID: {config['staff_role_id']}) for guild_id={guild.id}")
            return role
        else:
            print(f"get_staff_role: Role ID {config['staff_role_id']} not found in guild_id={guild.id}")
    else:
        print(f"get_staff_role: No staff_role_id found in configuration")
    return None

def get_category_id():
    """Get category ID from JSON configuration"""
    config = get_config()
    if config:
        category_id = config.get("ticket_category_id")
        if category_id:
            print(f"get_category_id: Found category_id={category_id}")
            return int(category_id)
    print(f"get_category_id: No ticket_category_id found in configuration")
    return None

def get_welcome_embed_data():
    """Get welcome embed data from JSON configuration"""
    config = get_config()
    if config and config.get("welcome_embed"):
        print(f"get_welcome_embed_data: Found welcome embed data")
        return config["welcome_embed"]
    print(f"get_welcome_embed_data: No welcome embed data found in configuration")
    return None

def get_panel_embed_data():
    """Get panel embed data from JSON configuration"""
    config = get_config()
    if config and config.get("panel_embed"):
        print(f"get_panel_embed_data: Found panel embed data")
        return config["panel_embed"]
    print(f"get_panel_embed_data: No panel embed data found in configuration")
    return None

def get_button_data():
    """Get button label and color from JSON configuration"""
    config = get_config()
    if config:
        button_label = config.get("button_label", "🎟️ Create Ticket")
        button_color = config.get("button_color", "primary")
        print(f"get_button_data: Found button data: label={button_label}, color={button_color}")
        return button_label, button_color
    print(f"get_button_data: No button data found in configuration, using defaults")
    return "🎟️ Create Ticket", "primary"

async def send_ticket_panel(bot):
    """Send ticket panel to configured channel on bot startup"""
    from .ticket import TicketPanelView
    
    config = get_config()
    if not config:
        print("send_ticket_panel: No configuration found")
        return
    
    server_id = config.get("server_id")
    channel_id = config.get("ticket_channel_id")
    
    if not server_id or not channel_id:
        print("send_ticket_panel: Missing server_id or ticket_channel_id in configuration")
        return
    
    try:
        guild = bot.get_guild(int(server_id))
        if not guild:
            print(f"send_ticket_panel: Guild {server_id} not found")
            return
        
        channel = guild.get_channel(int(channel_id))
        if not channel:
            print(f"send_ticket_panel: Channel {channel_id} not found in guild {server_id}")
            return
        
        # Get panel embed data
        panel_embed_data = get_panel_embed_data()
        if not panel_embed_data:
            print("send_ticket_panel: No panel embed data found")
            return
        
        # Get button data
        button_label, button_color = get_button_data()
        button_style = discord.ButtonStyle.primary
        if button_color == "success":
            button_style = discord.ButtonStyle.success
        elif button_color == "danger":
            button_style = discord.ButtonStyle.danger
        elif button_color == "secondary":
            button_style = discord.ButtonStyle.secondary
        
        # Create panel embed
        panel_embed = discord.Embed.from_dict(panel_embed_data)
        
        # Send panel to channel
        await channel.send(
            embed=panel_embed,
            view=TicketPanelView(button_label, button_style)
        )
        
        print(f"send_ticket_panel: Ticket panel sent successfully to #{channel.name} in {guild.name}")
        
    except Exception as e:
        print(f"send_ticket_panel: Error sending ticket panel: {str(e)}")

async def get_linked_accounts(discord_id):
    """Get linked accounts for a Discord user"""
    if accounts_db is None:
        print("Error: MongoDB not initialized for linked accounts")
        return []
    
    try:
        linked_players_collection = accounts_db.linked_players
        result = await linked_players_collection.find_one({"discord_id": str(discord_id)})
        if result:
            # Combine verified and unverified accounts
            verified = result.get("verified", [])
            unverified = result.get("unverified", [])
            all_accounts = verified + unverified
            print(f"get_linked_accounts: Found {len(all_accounts)} accounts for user {discord_id}")
            return all_accounts
        print(f"get_linked_accounts: No linked accounts found for user {discord_id}")
        return []
    except Exception as e:
        print(f"Error fetching linked accounts for user {discord_id}: {e}")
        return []

class TicketProfileViewWithSwitcher(discord.ui.View):
    def __init__(self, player_data, selected_accounts, current_view="Profile Overview"):
        super().__init__(timeout=None)
        self.player_data = player_data
        self.player_tag = player_data.get("tag", "")
        self.current_view = current_view
        self.selected_accounts = selected_accounts

        # Add the regular view selector first (row 0)
        self.add_item(TicketViewSelector(player_data, current_view))
        # Then add account switcher dropdown below (row 1)
        self.add_item(ProfileAccountSwitcher(selected_accounts, player_data))

class ProfileAccountSwitcher(discord.ui.Select):
    def __init__(self, selected_accounts, current_player_data):
        current_tag = current_player_data.get("tag", "")
        
        # Create options from selected accounts only
        options = []
        for account in selected_accounts[:25]:  # Discord limit of 25 options
            is_current = account["tag"] == current_tag
            options.append(discord.SelectOption(
                label=f"{account['name']} ({account['tag']})",
                value=account["tag"],
                description="Currently viewing" if is_current else f"Switch to {account['name']}",
                default=is_current
            ))
        
        super().__init__(
            placeholder="Switch account...",
            min_values=1,
            max_values=1,
            options=options,
            row=1
        )
        self.selected_accounts = selected_accounts
    
    async def callback(self, interaction: discord.Interaction):
        selected_tag = self.values[0]
        
        # Find the selected account
        selected_account = None
        for account in self.selected_accounts:
            if account["tag"] == selected_tag:
                selected_account = account
                break
        
        if not selected_account:
            await interaction.response.send_message("Account not found.", ephemeral=True)
            return
        
        # Get fresh player data for the selected account
        player_data = await get_coc_player(selected_tag)
        if player_data is None:
            await interaction.response.send_message("Failed to fetch player data for selected account.", ephemeral=True)
            return
        
        # Add Discord user info to player data
        player_data["discord_info"] = f"<@{interaction.user.id}>"
        
        # Update the view with new player data
        if self.view.current_view == "Profile Overview":
            new_embed = PlayerEmbeds.player_info(player_data)
        else:
            new_embed = PlayerEmbeds.unit_embed(player_data)
            
        new_view = TicketProfileViewWithSwitcher(player_data, self.selected_accounts, self.view.current_view)
        
        await interaction.response.edit_message(embed=new_embed, view=new_view)
