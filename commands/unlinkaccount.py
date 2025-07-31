import disnake
import os
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE") or "default_database"

# Initialize MongoDB client
mongodb_client = AsyncIOMotorClient(MONGODB_URI)
db = mongodb_client[MONGODB_DATABASE]

async def get_coc_player(player_tag):
    url = f"https://cocproxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            print(f"get_coc_player failed with status: {resp.status}")  # Debug log
            return None

async def get_linked_players(discord_id):
    try:
        linked_players_collection = db.linked_players
        result = await linked_players_collection.find_one({"discord_id": discord_id})
        if result:
            return result
        return {"discord_id": discord_id, "verified": [], "unverified": []}
    except Exception as e:
        print(f"MongoDB get_linked_players error: {e}")
        return {"discord_id": discord_id, "verified": [], "unverified": []}

async def save_linked_players(data):
    try:
        linked_players_collection = db.linked_players
        await linked_players_collection.replace_one({"discord_id": data["discord_id"]}, data, upsert=True)
    except Exception as e:
        print(f"MongoDB save_linked_players error: {e}")

def setup(bot):
    async def player_tag_autocomplete(interaction: disnake.ApplicationCommandInteraction, current: str):
        user_data = await get_linked_players(str(interaction.user.id))
        accounts = user_data.get("verified", []) + user_data.get("unverified", [])
        return [
            disnake.disnake.OptionChoice(
                name=f"{acc.get('name', acc.get('tag', 'Unknown'))} ({acc.get('tag', 'Unknown')})",
                value=acc.get('tag', '')
            )
            for acc in accounts
            if current.lower() in acc.get('tag', '').lower() or current.lower() in acc.get('name', '').lower()
        ][:25]

    @bot.slash_command(name="unlinkaccount", description="Unlink one of your account.")
    async def unlinkaccount_command(interaction: disnake.ApplicationCommandInteraction, tag: str):
        await interaction.response.defer()

        # Normalize and clean the tag
        player_tag = tag.upper().replace("O", "0")
        if not player_tag.startswith("#"):
            player_tag = "#" + player_tag

        user_id = str(interaction.user.id)
        user_data = await get_linked_players(user_id)

        verified_tags = [acc.get("tag") for acc in user_data.get("verified", [])]
        unverified_tags = [acc.get("tag") for acc in user_data.get("unverified", [])]
        
        if player_tag not in verified_tags and player_tag not in unverified_tags:
            embed = disnake.Embed(
                title="Unlink Error",
                description=f"**{player_tag}** is not linked to your Discord.",
                color=0xcccccc
            )
            await interaction.followup.send(embed=embed)
            return

        # Remove the tag from verified/unverified
        user_data["verified"] = [acc for acc in user_data.get("verified", []) if acc.get("tag") != player_tag]
        user_data["unverified"] = [acc for acc in user_data.get("unverified", []) if acc.get("tag") != player_tag]

        await save_linked_players(user_data)

        # Success response
        embed = disnake.Embed(
            title="Unlink Success",
            description=f"Successfully unlinked **{player_tag}** from your account.",
            color=0xcccccc
        )
        await interaction.followup.send(embed=embed)
    
    # Add autocomplete for the tag parameter
    @unlinkaccount_command.autocomplete("tag")
    async def unlink_tag_autocomplete_wrapper(interaction: disnake.ApplicationCommandInteraction, current: str):
        return await player_tag_autocomplete(interaction, current)