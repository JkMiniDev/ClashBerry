import os
import disnake
import aiohttp
import json
from motor.motor_asyncio import AsyncIOMotorClient

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE") or "default_database" or "default_database"

# Initialize MongoDB client
mongodb_client = AsyncIOMotorClient(MONGODB_URI)
db = mongodb_client[MONGODB_DATABASE]

async def get_coc_player(player_tag):
    url = f"https://cocproxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                print(f"get_coc_player response status: {resp.status}")  # Debug log
                if resp.status == 200:
                    return await resp.json()
                print(f"get_coc_player failed with status: {resp.status}")  # Debug log
                try:
                    print(f"get_coc_player response body: {await resp.json()}")  # Debug log
                except:
                    print("get_coc_player: No JSON response available")  # Debug log
                return None
        except aiohttp.ClientError as e:
            print(f"get_coc_player network error: {e}")  # Debug log
            return None

async def verify_coc_token(player_tag, token):
    url = f"https://cocproxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}/verifytoken"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    payload = {"token": token}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, json=payload) as resp:
                print(f"Token verification response status: {resp.status}")  # Debug log
                if resp.status == 200:
                    data = await resp.json()
                    print(f"Token verification response body: {data}")  # Debug log
                    return data.get("status") == "ok"
                elif resp.status == 403:
                    print("Token verification failed: Invalid API token")  # Debug log
                    return False
                elif resp.status == 429:
                    print("Token verification failed: Rate limit exceeded")  # Debug log
                    return False
                elif resp.status == 400:
                    print("Token verification failed: Invalid player token or malformed request")  # Debug log
                    return False
                else:
                    print(f"Token verification failed with status: {resp.status}")  # Debug log
                    try:
                        print(f"Token verification response body: {await resp.json()}")  # Debug log
                    except:
                        print("Token verification: No JSON response available")  # Debug log
                    return False
        except aiohttp.ClientError as e:
            print(f"Token verification network error: {e}")  # Debug log
            return False

async def get_linked_players(discord_id):
    try:
        linked_players_collection = db.linked_players
        result = await linked_players_collection.find_one({"discord_id": discord_id})
        if result:
            return result
        return {"discord_id": discord_id, "unverified": [], "verified": []}
    except Exception as e:
        print(f"MongoDB get_linked_players error: {e}")  # Debug log
        return {"discord_id": discord_id, "unverified": [], "verified": []}

async def save_linked_players(data):
    try:
        linked_players_collection = db.linked_players
        await linked_players_collection.replace_one({"discord_id": data["discord_id"]}, data, upsert=True)
    except Exception as e:
        print(f"MongoDB save_linked_players error: {e}")  # Debug log

async def remove_tag_from_other_users(player_tag, current_discord_id):
    try:
        linked_players_collection = db.linked_players
        cursor = linked_players_collection.find({})
        async for user in cursor:
            if user["discord_id"] == current_discord_id:
                continue
            updated = False
            # Check if tag exists in verified list (now as objects)
            user["verified"] = [acc for acc in user.get("verified", []) if acc.get("tag") != player_tag]
            user["unverified"] = [acc for acc in user.get("unverified", []) if acc.get("tag") != player_tag]
            # Always update since we're filtering the lists
            await linked_players_collection.replace_one({"discord_id": user["discord_id"]}, user)
    except Exception as e:
        print(f"MongoDB remove_tag_from_other_users error: {e}")  # Debug log

def setup(bot):
    @bot.slash_command(name="linkaccount", description="Link a account to a Discord user.")
    async def linkaccount_command(
        interaction: disnake.ApplicationCommandInteraction, 
        tag: str,
        user: disnake.User = None,
        api_token: str = None
    ):
        await interaction.response.defer()

        # Normalize player tag
        player_tag = tag.upper().replace("O", "0")
        if not player_tag.startswith("#"):
            player_tag = "#" + player_tag

        # Fetch player data
        player_data = await get_coc_player(player_tag)
        if not player_data:
            embed = disnake.Embed(title="Link Failed", description="No account found for the provided tag.", color=0xcccccc)
            await interaction.followup.send(embed=embed)
            return
        player_name = player_data.get("name", "?")

        # Determine target user
        target_user = user if user else interaction.user
        target_user_id = str(target_user.id)

        # Get user data from MongoDB
        user_data = await get_linked_players(target_user_id)

        # Check if tag is already linked to the interaction user and no API token provided
        all_linked_tags = [acc.get("tag") for acc in user_data.get("verified", [])] + [acc.get("tag") for acc in user_data.get("unverified", [])]
        if not api_token and player_tag in all_linked_tags and target_user_id == str(interaction.user.id):
            embed = disnake.Embed(
                title="Link Error",
                description=f"**{player_name} ({player_tag})** is already linked with your account.",
                color=0xcccccc
            )
            await interaction.followup.send(embed=embed)
            return

        # Check if tag is already linked to another user
        linked_players_collection = db.linked_players
        cursor = linked_players_collection.find({})
        async for user_data_other in cursor:
            other_linked_tags = [acc.get("tag") for acc in user_data_other.get("verified", [])] + [acc.get("tag") for acc in user_data_other.get("unverified", [])]
            if user_data_other["discord_id"] != target_user_id and player_tag in other_linked_tags:
                if not api_token:
                    embed = disnake.Embed(
                        title="Link Error",
                        description=f"**{player_name} ({player_tag})** is already linked to another user. If you own this account, use an API token to link.",
                        color=0xcccccc
                    )
                    await interaction.followup.send(embed=embed)
                    return

        # Handle API token verification
        if api_token:
            is_token_valid = await verify_coc_token(player_tag, api_token)
            if not is_token_valid:
                embed = disnake.Embed(
                    title="Link Failed",
                    description="Invalid API token. Token can be found in in-game setting.",
                    color=0xcccccc
                )
                await interaction.followup.send(embed=embed)
                return
            # Remove tag from other users if verified
            await remove_tag_from_other_users(player_tag, target_user_id)
            # Move from unverified to verified if already linked, or add to verified
            user_data["unverified"] = [acc for acc in user_data.get("unverified", []) if acc.get("tag") != player_tag]
            verified_tags = [acc.get("tag") for acc in user_data.get("verified", [])]
            if player_tag not in verified_tags:
                user_data["verified"].append({"tag": player_tag, "name": player_name})
            # Save to MongoDB
            await save_linked_players(user_data)
            # Send success embed for verified link
            embed = disnake.Embed(
                title="Link Success",
                description=f"**{player_name} ({player_tag})** linked successfully with token to {target_user.mention}",
                color=0xcccccc
            )
            await interaction.followup.send(embed=embed)
            return

        # Add to unverified if no token provided and not already linked
        unverified_tags = [acc.get("tag") for acc in user_data.get("unverified", [])]
        verified_tags = [acc.get("tag") for acc in user_data.get("verified", [])]
        if player_tag not in unverified_tags and player_tag not in verified_tags:
            user_data["unverified"].append({"tag": player_tag, "name": player_name})
            # Save to MongoDB
            await save_linked_players(user_data)
            # Send success embed for unverified link
            embed = disnake.Embed(
                title="Link Success",
                description=f"**{player_name} ({player_tag})** Linked successfully to {target_user.mention}",
                color=0xcccccc
            )
            await interaction.followup.send(embed=embed)