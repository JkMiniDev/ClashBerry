import os
import discord
import aiohttp
from supabase import create_client, Client

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Emoji table for Town Hall levels 1 to 17 (Unicode emojis)
TH_EMOJI_MAP = {
    1: "<:TH1:1389337801044131933>",   # Basic house emoji for TH1
    2: "<:TH2:1389338126907998238>",   # Slightly upgraded house for TH2
    3: "<:TH3:1389338161372729556>",  # Small village house for TH3
    4: "<:TH4:1389338196155830373>",   # Post office style for TH4
    5: "<:TH5:1389338267044020375>",   # Hospital-like for TH5
    6: "<:TH6:1389338294055079956>",   # Castle for TH6
    7: "<:TH7:1389338322639523910>",   # Mosque-like for TH7
    8: "<:TH8:1389338353907929278>",   # Japanese castle for TH8
    9: "<:TH9:1389338445863714826>",   # Temple for TH9
    10: "<:TH10:1389337837756743770>",  # Classical building for TH10
    11: "<:TH11:1389337873526030517>",  # Tower for TH11
    12: "<:TH12:1389337901132677202>",  # Stadium-like for TH12
    13: "<:TH13:1389337944837591152>",  # Statue for TH13
    14: "<:TH14:1389337974185136189>",  # Moai for TH14
    15: "<:TH15:1389338002114744362>",  # Ancient urn for TH15
    16: "<:TH16:1389338032766980247>",  # Tool for TH16
    17: "<:TH17:1389338065650319430>"   # Hammer for TH17
}

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

async def get_linked_players(discord_id):
    try:
        response = supabase.table("linked_players").select("*").eq("discord_id", discord_id).execute()
        if response.data:
            return response.data[0]
        return {"discord_id": discord_id, "unverified": [], "verified": []}
    except Exception as e:
        print(f"Supabase get_linked_players error: {e}")  # Debug log
        return {"discord_id": discord_id, "unverified": [], "verified": []}

def setup(bot):
    @bot.tree.command(name="accounts", description="Show a user's linked accounts.")
    @discord.app_commands.describe(
        user="Show linked accounts for a specific Discord user (optional)"
    )
    async def accounts_command(interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()

        # Determine target user
        target_user = user if user else interaction.user
        target_user_id = str(target_user.id)

        # Get user data from Supabase
        user_data = await get_linked_players(target_user_id)

        # Initialize embed
        embed = discord.Embed(
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

        # Fetch player data for each account and store with TH level for sorting
        accounts_list = []
        account_data = []
        async with aiohttp.ClientSession() as session:
            for player_tag in all_accounts:
                player_data = await get_coc_player(player_tag)
                if player_data:
                    player_name = player_data.get("name", "Unknown")
                    th_level = player_data.get("townHallLevel", 1)
                    th_emoji = TH_EMOJI_MAP.get(th_level, "❓")  # Default to question mark if not found
                    is_verified = player_tag in verified_accounts
                    verification_mark = " <:Verified:1390721846420439051>" if is_verified else ""
                    account_data.append({
                        "th_level": th_level,
                        "display": f"{th_emoji} {player_name} ({player_tag}){verification_mark}"
                    })
                else:
                    account_data.append({
                        "th_level": 0,  # Unknown accounts get lowest priority
                        "display": f"❓ Unknown ({player_tag})"
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