import os
import json
import aiohttp
import base64
from urllib.parse import urlparse, parse_qs
from supabase import create_client, Client
from dotenv import load_dotenv
import discord

load_dotenv()

COC_API_TOKEN = os.getenv("API_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_guild_data(guild_id, panel_name=None):
    """Get guild data from Supabase, optionally filter by panel name"""
    try:
        query = supabase.table("guild_settings").select("*").eq("guild_id", str(guild_id))
        if panel_name:
            query = query.eq("panel_name", panel_name)
        response = query.execute()
        if response.data:
            print(f"get_guild_data: Found data for guild_id={guild_id}, panel_name={panel_name}: {response.data[0]}")
            return response.data[0]
        print(f"get_guild_data: No data found for guild_id={guild_id}, panel_name={panel_name}")
        return None
    except Exception as e:
        print(f"Error fetching guild data for guild_id={guild_id}, panel_name={panel_name}: {e}")
        return None

async def get_panel_names(guild_id):
    """Get list of panel names for a guild (for autocomplete)"""
    try:
        response = supabase.table("guild_settings").select("panel_name").eq("guild_id", str(guild_id)).execute()
        panel_names = [row["panel_name"] for row in response.data] if response.data else []
        print(f"get_panel_names: Found panel names for guild_id={guild_id}: {panel_names}")
        return panel_names
    except Exception as e:
        print(f"Error fetching panel names for guild_id={guild_id}: {e}")
        return []

async def save_guild_data(guild_id, panel_name, staff_role_id=None, category_id=None, panel_embed_data=None, welcome_embed_data=None, button_label=None, button_color=None):
    """Save guild and panel data to Supabase"""
    try:
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

        # Check if panel exists for guild
        existing = await get_guild_data(guild_id)
        if existing:
            # Update existing record
            supabase.table("guild_settings").update(data).eq("guild_id", str(guild_id)).execute()
            print(f"save_guild_data: Updated existing record for guild_id={guild_id}")
        else:
            # Insert new record
            supabase.table("guild_settings").insert(data).execute()
            print(f"save_guild_data: Inserted new record for guild_id={guild_id}")
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
    """Get welcome embed data from Supabase"""
    guild_data = await get_guild_data(guild_id, panel_name)
    if guild_data:
        print(f"get_welcome_embed_data: Found welcome embed data for guild_id={guild_id}, panel_name={panel_name}")
        return guild_data.get("welcome_embed_data")
    print(f"get_welcome_embed_data: No welcome embed data for guild_id={guild_id}, panel_name={panel_name}")
    return None

async def get_panel_embed_data(guild_id, panel_name):
    """Get panel embed data from Supabase"""
    guild_data = await get_guild_data(guild_id, panel_name)
    if guild_data:
        print(f"get_panel_embed_data: Found panel embed data for guild_id={guild_id}, panel_name={panel_name}")
        return guild_data.get("panel_embed_data")
    print(f"get_panel_embed_data: No panel embed data for guild_id={guild_id}, panel_name={panel_name}")
    return None

async def get_button_data(guild_id, panel_name):
    """Get button label and color from Supabase"""
    guild_data = await get_guild_data(guild_id, panel_name)
    if guild_data:
        print(f"get_button_data: Found button data for guild_id={guild_id}, panel_name={panel_name}: label={guild_data.get('button_label')}, color={guild_data.get('button_color')}")
        return guild_data.get("button_label"), guild_data.get("button_color")
    print(f"get_button_data: No button data for guild_id={guild_id}, panel_name={panel_name}")
    return None, None

async def delete_guild_data(guild_id, panel_name=None):
    """Delete guild or panel data from Supabase"""
    try:
        query = supabase.table("guild_settings").delete().eq("guild_id", str(guild_id))
        if panel_name:
            query = query.eq("panel_name", panel_name)
        response = query.execute()
        print(f"delete_guild_data: Deleted data for guild_id={guild_id}, panel_name={panel_name}")
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
    """Display Clash of Clans player profile"""
    th_level = player_data.get("townHallLevel", "?")
    name = player_data.get("name", "?")
    tag = player_data.get("tag", "?")
    exp_level = player_data.get("expLevel", "?")
    trophies = player_data.get("trophies", "?")
    clan = player_data.get("clan", {}).get("name", "None")
    embed = discord.Embed(
        title=f"{name} ({tag})",
        color=discord.Color.green(),
        description=(
            f"TH Level: **{th_level}**\n"
            f"Exp Level: **{exp_level}**\n"
            f"Trophies: **{trophies}**\n"
            f"Clan: **{clan}**"
        )
    )
    if "league" in player_data and "iconUrls" in player_data["league"]:
        icon = player_data["league"]["iconUrls"].get("medium")
        if icon:
            embed.set_thumbnail(url=icon)
    await interaction.response.send_message(embed=embed, ephemeral=True)