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

async def show_profile(player_tag, interaction_user=None):
    """Show Clash of Clans player profile with real-time data"""
    # Fetch real player data from CoC API
    player_data = await get_coc_player(player_tag)
    
    if not player_data:
        # Fallback embed if API fails
        embed = disnake.Embed(
            title="❌ Player Not Found",
            description=f"**Player Tag:** {player_tag}\n**Status:** Could not fetch player data\n**Discord User:** {interaction_user.mention if interaction_user else 'Unknown'}",
            color=0xff0000
        )
        return embed
    
    # Create detailed player profile embed
    player_name = player_data.get('name', 'Unknown')
    th_level = player_data.get('townHallLevel', '?')
    exp_level = player_data.get('expLevel', '?')
    trophies = player_data.get('trophies', '?')
    best_trophies = player_data.get('bestTrophies', '?')
    
    # Create clickable title URL
    title_url = None
    if player_tag.startswith('#'):
        tag_clean = player_tag[1:]
        title_url = f"https://link.clashofclans.com/?action=OpenPlayerProfile&tag=%23{tag_clean}"
    
    embed = disnake.Embed(
        title=f"{player_name} ({player_tag})",
        url=title_url,
        color=0x00ff00,
        timestamp=disnake.utils.utcnow()
    )
    
    # Basic info
    embed.add_field(
        name="🏰 Town Hall & Level",
        value=f"**TH Level:** {th_level}\n**XP Level:** {exp_level}",
        inline=True
    )
    
    embed.add_field(
        name="🏆 Trophies",
        value=f"**Current:** {trophies:,}\n**Best:** {best_trophies:,}",
        inline=True
    )
    
    # Clan info
    clan = player_data.get("clan", {})
    clan_name = clan.get("name", "No Clan")
    role = player_data.get("role", "member")
    role_map = {
        "admin": "Elder",
        "coLeader": "Co-Leader", 
        "leader": "Leader",
        "member": "Member"
    }
    clan_role = role_map.get(role, "Member")
    
    if clan_name != "No Clan" and clan.get("tag"):
        clan_tag = clan["tag"].replace("#", "")
        clan_url = f"https://link.clashofclans.com/?action=OpenClanProfile&tag=%23{clan_tag}"
        clan_value = f"[{clan_name}]({clan_url})\n**Role:** {clan_role}"
    else:
        clan_value = "Not in a clan"
    
    embed.add_field(name="⚔️ Clan", value=clan_value, inline=False)
    
    # Season stats
    donations = player_data.get('donations', 0)
    donations_received = player_data.get('donationsReceived', 0)
    attack_wins = player_data.get('attackWins', 0)
    defense_wins = player_data.get('defenseWins', 0)
    
    season_stats = f"**Donated:** {donations:,}\n**Received:** {donations_received:,}\n**Attack Wins:** {attack_wins:,}\n**Defense Wins:** {defense_wins:,}"
    embed.add_field(name="📊 Season Stats", value=season_stats, inline=True)
    
    # War stats
    war_stars = player_data.get('warStars', 0)
    achievements = {a["name"]: a["value"] for a in player_data.get("achievements", [])}
    cwl_stars = achievements.get('War League Legend', 0)
    
    war_stats = f"**War Stars:** {war_stars:,}\n**CWL Stars:** {cwl_stars:,}"
    war_preference = player_data.get("warPreference", "").lower()
    if war_preference == "in":
        war_stats += "\n**War Opt:** ✅ In"
    elif war_preference == "out":
        war_stats += "\n**War Opt:** ❌ Out"
    
    embed.add_field(name="⚔️ War Stats", value=war_stats, inline=True)
    
    # League badge as thumbnail
    league = player_data.get("league", {})
    if league and league.get("iconUrls", {}).get("medium"):
        embed.set_thumbnail(url=league["iconUrls"]["medium"])
    
    # Discord user info
    if interaction_user:
        embed.add_field(name="👤 Discord User", value=interaction_user.mention, inline=False)
    
    embed.set_footer(text="Player data • Live from Clash of Clans API")
    
    return embed

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