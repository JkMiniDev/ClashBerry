import os
import discord
import aiohttp
from supabase import create_client, Client

# Environment variables
COC_API_TOKEN = os.getenv("API_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def get_coc_clan(clan_tag):
    url = f"https://cocproxy.royaleapi.dev/v1/clans/{clan_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
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
    @bot.tree.command(name="addclan", description="Link a clan to this server.")
    @discord.app_commands.describe(tag="Clan tag (e.g. #2Q82LRL)")
    async def addclan_command(interaction: discord.Interaction, tag: str):
        # Admin check
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="Link Error",
                description="You don't have permission to add clan in the server.",
                color=0xcccccc
            )
            await interaction.response.send_message(embed=embed)
            return

        await interaction.response.defer()
        clan_tag = tag.upper().replace("O", "0")
        if not clan_tag.startswith("#"):
            clan_tag = "#" + clan_tag

        clan_data = await get_coc_clan(clan_tag)
        if not clan_data:
            embed = discord.Embed(
                title="Link Error",
                description="No clan found for the provided tag.",
                color=0xcccccc
            )
            await interaction.followup.send(embed=embed)
            return
        clan_name = clan_data.get("name", "?")

        data = await get_linked_clans(str(interaction.guild.id))
        guild_id = str(interaction.guild.id)
        if any(acc['tag'].upper() == clan_tag for acc in data["clans"]):
            embed = discord.Embed(
                title="Link Error",
                description=f"**{clan_name} {clan_tag}** already linked to this server.",
                color=0xcccccc
            )
            await interaction.followup.send(embed=embed)
            return
        data["clans"].append({"name": clan_name, "tag": clan_tag})
        await save_linked_clans(data)
        embed = discord.Embed(
            title="Link Success",
            description=f"**{clan_name} {clan_tag}** linked successfully to this server.",
            color=0xcccccc
        )
        await interaction.followup.send(embed=embed)