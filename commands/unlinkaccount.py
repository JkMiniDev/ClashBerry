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
        response = supabase.table("linked_players").select("*").eq("discord_id", discord_id).execute()
        if response.data:
            return response.data[0]
        return {"discord_id": discord_id, "verified": [], "unverified": []}
    except Exception as e:
        print(f"Supabase get_linked_players error: {e}")
        return {"discord_id": discord_id, "verified": [], "unverified": []}

async def save_linked_players(data):
    try:
        supabase.table("linked_players").upsert(data).execute()
    except Exception as e:
        print(f"Supabase save_linked_players error: {e}")

def setup(bot):
    async def player_tag_autocomplete(interaction: discord.Interaction, current: str):
        user_data = await get_linked_players(str(interaction.user.id))
        accounts = user_data.get("verified", []) + user_data.get("unverified", [])
        options = []
        for tag in accounts:
            player_data = await get_coc_player(tag)
            player_name = player_data.get("name", tag) if player_data else tag
            options.append({"name": player_name, "tag": tag})
        return [
            discord.app_commands.Choice(
                name=f"{acc['name']} ({acc['tag']})",
                value=acc['tag']
            )
            for acc in options
            if current.lower() in acc['tag'].lower() or current.lower() in acc['name'].lower()
        ][:25]

    @bot.tree.command(name="unlinkaccount", description="Unlink one of your account.")
    @discord.app_commands.describe(tag="Player tag (e.g. #2Q82LRL)")
    @discord.app_commands.autocomplete(tag=player_tag_autocomplete)
    async def unlinkaccount_command(interaction: discord.Interaction, tag: str):
        await interaction.response.defer()

        # Normalize and clean the tag
        player_tag = tag.upper().replace("O", "0")
        if not player_tag.startswith("#"):
            player_tag = "#" + player_tag

        user_id = str(interaction.user.id)
        user_data = await get_linked_players(user_id)

        if player_tag not in user_data.get("verified", []) and player_tag not in user_data.get("unverified", []):
            embed = discord.Embed(
                title="Unlink Error",
                description=f"**{player_tag}** is not linked to your Discord.",
                color=0xcccccc
            )
            await interaction.followup.send(embed=embed)
            return

        # Remove the tag from verified/unverified
        if player_tag in user_data["verified"]:
            user_data["verified"].remove(player_tag)
        if player_tag in user_data["unverified"]:
            user_data["unverified"].remove(player_tag)

        await save_linked_players(user_data)

        # Success response
        embed = discord.Embed(
            title="Unlink Success",
            description=f"Successfully unlinked **{player_tag}** from your account.",
            color=0xcccccc
        )
        await interaction.followup.send(embed=embed)