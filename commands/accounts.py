import os
import disnake
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import json

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE") or "default_database"

# Initialize MongoDB client
mongodb_client = AsyncIOMotorClient(MONGODB_URI)
db = mongodb_client[MONGODB_DATABASE]

# Load TH emojis from JSON
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'emoji', 'town_halls.json'), 'r') as f:
    TH_EMOJI_MAP = json.load(f)

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

async def update_player_name_if_changed(player_tag, new_name):
    """Update player name in database if it has changed"""
    try:
        linked_players_collection = db.linked_players
        cursor = linked_players_collection.find({})
        async for record in cursor:
            updated = False
            
            # Update verified accounts
            for account in record.get("verified", []):
                if account.get("tag") == player_tag and account.get("name") != new_name:
                    account["name"] = new_name
                    updated = True
            
            # Update unverified accounts
            for account in record.get("unverified", []):
                if account.get("tag") == player_tag and account.get("name") != new_name:
                    account["name"] = new_name
                    updated = True
            
            # Save if updated
            if updated:
                await linked_players_collection.replace_one({"discord_id": record["discord_id"]}, record)
                print(f"Updated player name for {player_tag} to {new_name}")
                
    except Exception as e:
        print(f"Error updating player name: {e}")

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

def setup(bot):
    @bot.slash_command(name="accounts", description="Show a user's linked accounts.")
    async def accounts_command(
        interaction: disnake.ApplicationCommandInteraction, 
        user: disnake.User = None
    ):
        await interaction.response.defer()

        # Determine target user
        target_user = user if user else interaction.user
        target_user_id = str(target_user.id)

        # Get user data from MongoDB
        user_data = await get_linked_players(target_user_id)

        # Initialize embed
        embed = disnake.Embed(
            title="Linked Accounts",
            description=f"List of accounts {target_user.mention} has linked.",
            color=0xcccccc
        )

        # Combine verified and unverified accounts
        verified_accounts = user_data.get("verified", [])
        unverified_accounts = user_data.get("unverified", [])
        all_accounts = verified_accounts + unverified_accounts

        if not all_accounts:
            embed.add_field(
                name="Accounts List",
                value="No linked accounts found.",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return

        # Process accounts and fetch fresh data to check for name changes and get TH levels
        account_data = []
        names_updated = False
        
        for account in all_accounts:
            player_tag = account.get("tag", "")
            stored_name = account.get("name", "Unknown")
            is_verified = account in verified_accounts
            
            # Fetch fresh player data for TH level and name verification
            player_data = await get_coc_player(player_tag)
            if player_data:
                current_name = player_data.get("name", "Unknown")
                th_level = player_data.get("townHallLevel", 1)
                th_emoji = TH_EMOJI_MAP.get(str(th_level), "❓")
                
                # Check if name has changed and update database
                if current_name != stored_name and player_tag and current_name:
                    await update_player_name_if_changed(player_tag, current_name)
                    names_updated = True
                
                # Use current name (stored name might be outdated)
                verification_mark = " <:Verified:1390721846420439051>" if is_verified else ""
                account_data.append({
                    "th_level": th_level,
                    "display": f"{th_emoji} {current_name} ({player_tag}){verification_mark}"
                })
            else:
                # Fallback to stored name if API fails
                account_data.append({
                    "th_level": 0,  # Unknown accounts get lowest priority
                    "display": f"❓ {stored_name} ({player_tag})"
                })

        # Sort accounts by TH level in descending order
        account_data.sort(key=lambda x: x["th_level"], reverse=True)
        accounts_list = [account["display"] for account in account_data]

        # Add accounts to embed
        embed.add_field(
            name="Accounts List",
            value="\n".join(accounts_list) if accounts_list else "No valid accounts found.",
            inline=False
        )

        # Send embed
        await interaction.followup.send(embed=embed)