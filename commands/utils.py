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
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
ticket_config = None

def load_config():
    global ticket_config
    try:
        with open(config_path, 'r') as f:
            ticket_config = json.load(f)
        print(f"Ticket configuration loaded successfully from {config_path}")
    except FileNotFoundError:
        print(f"Warning: config.json not found at {config_path}")
        ticket_config = {}
    except Exception as e:
        print(f"Error loading config.json: {str(e)}")
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
    """Get welcome embed data from welcome.json file"""
    try:
        import json
        import os
        
        # Get the path to the welcome.json file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        welcome_path = os.path.join(current_dir, "embeds", "welcome.json")
        
        if os.path.exists(welcome_path):
            with open(welcome_path, 'r', encoding='utf-8') as f:
                welcome_data = json.load(f)
                print(f"get_welcome_embed_data: Found welcome embed data")
                return welcome_data
        else:
            print(f"get_welcome_embed_data: welcome.json file not found at {welcome_path}")
            return None
    except Exception as e:
        print(f"get_welcome_embed_data: Error reading welcome.json: {e}")
        return None

def get_panel_embed_data():
    """Get panel embed data from panel.json file"""
    try:
        import json
        import os
        
        # Get the path to the panel.json file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        panel_path = os.path.join(current_dir, "embeds", "panel.json")
        
        if os.path.exists(panel_path):
            with open(panel_path, 'r', encoding='utf-8') as f:
                panel_data = json.load(f)
                print(f"get_panel_embed_data: Found panel embed data")
                return panel_data
        else:
            print(f"get_panel_embed_data: panel.json file not found at {panel_path}")
            return None
    except Exception as e:
        print(f"get_panel_embed_data: Error reading panel.json: {e}")
        return None

def get_button_data():
    """Get button data from panel.json file"""
    try:
        panel_data = get_panel_embed_data()
        if panel_data and panel_data.get("button"):
            button_info = panel_data["button"]
            button_label = button_info.get("label", "🎟️ Create Ticket")
            button_color = button_info.get("color", "primary")
            print(f"get_button_data: Found button data: label={button_label}, color={button_color}")
            return {"label": button_label, "color": button_color}
        else:
            print(f"get_button_data: No button data found in panel.json, using defaults")
            return {"label": "🎟️ Create Ticket", "color": "primary"}
    except Exception as e:
        print(f"get_button_data: Error reading button data: {e}")
        return {"label": "🎟️ Create Ticket", "color": "primary"}

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
        button_data = get_button_data()
        button_label = button_data.get("label", "🎟️ Create Ticket")
        button_color = button_data.get("color", "primary")
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

async def get_discord_info_for_player(player_tag):
    """Get Discord info for a specific player tag (same as players.py)"""
    if accounts_db is None:
        print("Error: MongoDB not initialized for linked accounts")
        return "Not Linked"
    
    try:
        linked_players_collection = accounts_db.linked_players
        cursor = linked_players_collection.find({})
        async for record in cursor:
            verified_tags = [acc.get("tag") for acc in record.get("verified", [])]
            unverified_tags = [acc.get("tag") for acc in record.get("unverified", [])]
            
            if player_tag in verified_tags:
                discord_id = f"<@{record.get('discord_id', 'Not Linked')}>"
                verified_emoji = "<:Verified:1390721846420439051>"
                return f"{discord_id} {verified_emoji}"
            elif player_tag in unverified_tags:
                discord_id = f"<@{record.get('discord_id', 'Not Linked')}>"
                return discord_id
        return "Not Linked"
    except Exception as e:
        print(f"Error querying MongoDB for linked player: {str(e)}")
        return "Not Linked"


