import disnake
import os
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Initialize MongoDB client
mongodb_client = AsyncIOMotorClient(MONGODB_URI)
db = mongodb_client[MONGODB_DATABASE]

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
        linked_clans_collection = db.linked_clans
        result = await linked_clans_collection.find_one({"guild_id": guild_id})
        if result:
            return result
        return {"guild_id": guild_id, "clans": []}
    except Exception as e:
        print(f"MongoDB get_linked_clans error: {e}")  # Debug log
        return {"guild_id": guild_id, "clans": []}

async def save_linked_clans(data):
    try:
        linked_clans_collection = db.linked_clans
        await linked_clans_collection.replace_one({"guild_id": data["guild_id"]}, data, upsert=True)
    except Exception as e:
        print(f"MongoDB save_linked_clans error: {e}")  # Debug log

def setup(bot):
    async def clan_tag_autocomplete(interaction: disnake.Interaction, current: str):
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
            disnake.app_commands.Choice(
                name=f"{acc['name']} ({acc['tag']})",
                value=acc['tag']
            )
            for acc in options
            if current.lower() in acc['tag'].lower() or current.lower() in acc['name'].lower()
        ][:25]

    @bot.tree.command(name="removeclan", description="Remove a clan linked to this server.")
    @disnake.app_commands.describe(tag="Clan tag (e.g. #2Q82LRL)")
    @disnake.app_commands.autocomplete(tag=clan_tag_autocomplete)
    async def removeclan_command(interaction: disnake.Interaction, tag: str):
        # Admin check
        if not interaction.user.guild_permissions.administrator:
            embed = disnake.Embed(
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
            embed = disnake.Embed(
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
        embed = disnake.Embed(
            title="Remove Success",
            description=f"**{clan_name} ({clan_tag})** successfully removed from this server.",
            color=0xcccccc
        )
        await interaction.followup.send(embed=embed)