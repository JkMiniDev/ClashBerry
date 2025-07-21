import discord
import os
import aiohttp
from supabase import create_client, Client

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_coc_clan(clan_tag):
    url = f"https://cocproxy.royaleapi.dev/v1/clans/{clan_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            print(f"get_coc_clan failed with status: {resp.status}")  # Debug log
            return None

async def get_linked_clans(guild_id):
    try:
        response = supabase.table("linked_clans").select("*").eq("guild_id", guild_id).execute()
        if response.data:
            return response.data[0]
        return {"guild_id": guild_id, "clans": []}
    except Exception as e:
        print(f"Supabase get_linked_clans error: {e}")  # Debug log
        return {"guild_id": guild_id, "clans": []}

async def save_linked_clans(data):
    try:
        supabase.table("linked_clans").upsert(data).execute()
    except Exception as e:
        print(f"Supabase save_linked_clans error: {e}")  # Debug log

def setup(bot):
    async def clan_tag_autocomplete(interaction: discord.Interaction, current: str):
        # Admin check for autocomplete
        if not interaction.user.guild_permissions.administrator:
            return []

        guild_id = str(interaction.guild.id)
        data = await get_linked_clans(guild_id)
        clans = data.get("clans", [])
        options = []
        for clan in clans:
            clan_data = await get_coc_clan(clan['tag'])
            clan_name = clan_data.get("name", clan['tag']) if clan_data else clan['tag']
            options.append({"name": clan_name, "tag": clan['tag']})
        return [
            discord.app_commands.Choice(
                name=f"{acc['name']} ({acc['tag']})",
                value=acc['tag']
            )
            for acc in options
            if current.lower() in acc['tag'].lower() or current.lower() in acc['name'].lower()
        ][:25]

    @bot.tree.command(name="removeclan", description="Remove a clan linked to this server.")
    @discord.app_commands.describe(tag="Clan tag (e.g. #2Q82LRL)")
    @discord.app_commands.autocomplete(tag=clan_tag_autocomplete)
    async def removeclan_command(interaction: discord.Interaction, tag: str):
        # Admin check
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="Remove Error",
                description="You don't have permission to remove clan in the server.",
                color=0xcccccc
            )
            await interaction.response.send_message(embed=embed)
            return

        await interaction.response.defer()

        # Normalize and clean the tag
        clan_tag = tag.upper().replace("O", "0")
        if not clan_tag.startswith("#"):
            clan_tag = "#" + clan_tag

        guild_id = str(interaction.guild.id)
        data = await get_linked_clans(guild_id)
        clans = data.get("clans", [])
        if not any(clan['tag'].upper() == clan_tag for clan in clans):
            embed = discord.Embed(
                title="Remove Error",
                description="Provided clan is not linked to this server",
                color=0xcccccc
            )
            await interaction.followup.send(embed=embed)
            return

        # Fetch clan name for success message
        clan_data = await get_coc_clan(clan_tag)
        clan_name = clan_data.get("name", clan_tag) if clan_data else clan_tag

        # Remove the tag
        new_clans = [c for c in clans if c['tag'].upper() != clan_tag]
        data["clans"] = new_clans
        await save_linked_clans(data)

        # Success response
        embed = discord.Embed(
            title="Remove Success",
            description=f"**{clan_name} ({clan_tag})** successfully removed from this server.",
            color=0xcccccc
        )
        await interaction.followup.send(embed=embed)