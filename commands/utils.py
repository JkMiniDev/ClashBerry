import os
import json
import aiohttp
import disnake
from dotenv import load_dotenv

load_dotenv()

COC_API_TOKEN = os.getenv("COC_API_TOKEN")

# Load configuration from JSON file
def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found. Please create the configuration file.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing config.json: {e}")
        return None

def save_config(config_data):
    """Save configuration to config.json"""
    try:
        with open('config.json', 'w') as f:
            json.dump(config_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config.json: {e}")
        return False

async def get_guild_data():
    """Get guild configuration from JSON file"""
    return load_config()

async def get_staff_role(guild):
    """Get staff role from configuration"""
    config = load_config()
    if not config or not config.get("staff_role_id"):
        return None
    
    try:
        role = guild.get_role(int(config["staff_role_id"]))
        return role
    except (ValueError, TypeError):
        return None

async def get_category_id():
    """Get ticket category ID from configuration"""
    config = load_config()
    if not config:
        return None
    return config.get("category_id")

async def get_welcome_embed_data():
    """Get welcome embed data from configuration"""
    config = load_config()
    if not config:
        return None
    return config.get("welcome_embed")

async def get_panel_embed_data():
    """Get panel embed data from configuration"""
    config = load_config()
    if not config:
        return None
    return config.get("panel_embed")

async def get_button_data():
    """Get button configuration from JSON"""
    config = load_config()
    if not config:
        return "🎟️ Create Ticket", "primary"
    
    label = config.get("button_label", "🎟️ Create Ticket")
    color = config.get("button_color", "primary")
    return label, color

def create_embed_from_data(embed_data, **kwargs):
    """Create a Discord embed from configuration data"""
    if not embed_data:
        return None
    
    embed = disnake.Embed(
        title=embed_data.get("title", ""),
        description=embed_data.get("description", "").format(**kwargs),
        color=embed_data.get("color", 0x2f3136)
    )
    
    if "footer" in embed_data:
        embed.set_footer(text=embed_data["footer"].get("text", ""))
    
    if "thumbnail" in embed_data:
        embed.set_thumbnail(url=embed_data["thumbnail"])
        
    if "image" in embed_data:
        embed.set_image(url=embed_data["image"])
    
    return embed

async def get_coc_player(player_tag):
    """Fetch Clash of Clans player data from API"""
    if not COC_API_TOKEN:
        print("Error: COC_API_TOKEN not set in environment variables")
        return None
        
    url = f"https://api.clashofclans.com/v1/players/{player_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    player_data = await resp.json()
                    print(f"Successfully fetched player data for {player_tag}")
                    return player_data
                else:
                    print(f"Failed to fetch player data for {player_tag}, status: {resp.status}")
                    return None
    except Exception as e:
        print(f"Error fetching player data: {e}")
        return None

async def show_profile(interaction, player_data):
    """Display enhanced Clash of Clans player profile with dropdown menu"""
    embed = PlayerEmbeds.player_info(player_data)
    view = TicketProfileView(player_data)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Color mapping for button styles
BUTTON_COLOR_MAP = {
    "primary": disnake.ButtonStyle.primary,
    "secondary": disnake.ButtonStyle.secondary,
    "success": disnake.ButtonStyle.success,
    "danger": disnake.ButtonStyle.danger,
    "red": disnake.ButtonStyle.danger,
    "green": disnake.ButtonStyle.success,
    "blue": disnake.ButtonStyle.primary,
    "grey": disnake.ButtonStyle.secondary,
    "gray": disnake.ButtonStyle.secondary
}

def get_button_style(color_name):
    """Convert color name to Discord button style"""
    return BUTTON_COLOR_MAP.get(color_name.lower(), disnake.ButtonStyle.primary)

class PlayerEmbeds:
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
        try:
            embed.description = f"TH{th_level} • Level {exp_level} • 🏆 {trophies}"
        except Exception as e:
            print(f"Error setting embed description: {str(e)}")
            embed.description = f"TH{th_level} • Level {exp_level} • Trophies: {trophies}"

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
            f"Donated: {player_data.get('donations', 0)}\n"
            f"Received: {player_data.get('donationsReceived', 0)}\n"
            f"Attack Wins: {player_data.get('attackWins', 0)}\n"
            f"Defense Wins: {player_data.get('defenseWins', 0)}"
        )
        embed.add_field(name="Season Stats", value=season_stats, inline=False)

        # War Stats field
        achievements = {a["name"]: a["value"] for a in player_data.get("achievements", [])}
        war_preference_raw = player_data.get("warPreference")
        war_preference = war_preference_raw.capitalize() if war_preference_raw else ""
        war_lines = [
            f"War Stars: {player_data.get('warStars', '?')}",
            f"CWL Stars: {achievements.get('War League Legend', 0)}"
        ]
        if war_preference == "In":
            war_lines.append(f"Preference: ✅ In")
        elif war_preference == "Out":
            war_lines.append(f"Preference: ❌ Out")
        war_stats = "\n".join(war_lines)
        embed.add_field(name="War Stats", value=war_stats, inline=False)

        # Overall Stats (remaining achievements)
        overall_stats = (
            f"Best Trophy: {player_data.get('bestTrophies', '?')}\n"
            f"Attack Wins: {achievements.get('Conqueror', 0)}\n"
            f"Defense Wins: {achievements.get('Unbreakable', 0)}\n"
            f"Troops Donated: {achievements.get('Friend in Need', 0)}"
        )
        embed.add_field(name="Overall Stats", value=overall_stats, inline=False)

        # League icon (if available)
        icon = player_data.get("league", {}).get("iconUrls", {}).get("medium")
        if icon:
            embed.set_thumbnail(url=icon)
        
        return embed

    @staticmethod
    def army_overview(player_data):
        embed = disnake.Embed(
            title="Army Overview",
            color=0xcccccc
        )
        
        # Basic army info - simplified for now
        troops = player_data.get("troops", [])
        spells = player_data.get("spells", [])
        heroes = player_data.get("heroes", [])
        
        if troops:
            troop_info = "\n".join([f"{troop.get('name', 'Unknown')}: Level {troop.get('level', '?')}" 
                                   for troop in troops[:10]])  # Show first 10 troops
            embed.add_field(name="Troops", value=troop_info or "No troops", inline=True)
        
        if heroes:
            hero_info = "\n".join([f"{hero.get('name', 'Unknown')}: Level {hero.get('level', '?')}" 
                                  for hero in heroes])
            embed.add_field(name="Heroes", value=hero_info or "No heroes", inline=True)
        
        if spells:
            spell_info = "\n".join([f"{spell.get('name', 'Unknown')}: Level {spell.get('level', '?')}" 
                                   for spell in spells[:8]])  # Show first 8 spells
            embed.add_field(name="Spells", value=spell_info or "No spells", inline=False)
        
        return embed

class TicketViewSelector(disnake.ui.Select):
    def __init__(self, player_data, current_view):
        self.player_data = player_data
        options = [
            disnake.SelectOption(
                label="Profile Overview",
                description="Show player profile information",
                emoji="👤",
                default=(current_view == "Profile Overview")
            ),
            disnake.SelectOption(
                label="Army Overview",
                description="Show troops, spells, and heroes",
                emoji="⚔️",
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
            embed = PlayerEmbeds.army_overview(self.player_data)
        
        view = TicketProfileView(self.player_data, current_view=self.values[0])
        await interaction.response.edit_message(embed=embed, view=view)

class TicketProfileView(disnake.ui.View):
    def __init__(self, player_data, current_view="Profile Overview"):
        super().__init__(timeout=None)
        self.player_data = player_data
        self.player_tag = player_data.get("tag", "")
        self.current_view = current_view

        self.add_item(TicketViewSelector(player_data, current_view))