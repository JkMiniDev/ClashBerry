import os
import json
import aiohttp
import disnake

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

async def show_profile(player_tag, interaction_user=None):
    """Show player profile (placeholder for CoC API integration)"""
    # For now, return a simple embed since we don't have CoC API integration yet
    embed = disnake.Embed(
        title="Player Profile",
        description=f"Player Tag: {player_tag}",
        color=0x00ff00
    )
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