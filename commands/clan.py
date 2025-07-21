import os
import discord
import aiohttp
from supabase import create_client, Client
from datetime import datetime

TH_EMOJIS = {
    17: "<:TH17:1389338065650319430>",
    16: "<:TH16:1389338032766980247>",
    15: "<:TH15:1389338002114744362>",
    14: "<:TH14:1389337974185136189>",
    13: "<:TH13:1389337944837591152>",
    12: "<:TH12:1389337901132677202>",
    11: "<:TH11:1389337873526030517>",
    10: "<:TH10:1389337837756743770>",
    9:  "<:TH9:1389338445863714826>",
    8:  "<:TH8:1389338353907929278>",
    7:  "<:TH7:1389338322639523910>",
    6:  "<:TH6:1389338294055079956>",
    5:  "<:TH5:1389338267044020375>",
    4:  "<:TH4:1389338196155830373>",
    3:  "<:TH3:1389338161372729556>",
    2:  "<:TH2:1389338126907998238>",
    1:  "<:TH1:1389337801044131933>"
}

CAPITAL_HALL_EMOJIS = {
    10: "<:Capital_Hall10:1390930893706887268>", 9: "<:Capital_Hall9:1390930868222169128>", 8: "<:Capital_Hall8:1390930846952853504>", 7: "<:Capital_Hall7:1390930821845745674>",
    6: "<:Capital_Hall6:1390930789826564207>", 5: "<:Capital_Hall5:1390930760105459764>", 4: "<:Capital_Hall4:1390930726928646174>", 3: "<:Capital_Hall3:1390930691633451119>", 2: "<:Capital_Hall2:1390930665817767937>", 1: "<:Capital_Hall1:1390930636814028832>"
}

LEAGUE_EMOJIS = {
    "Unranked": "<:Unranked:1390942114875179079>",
    "Bronze League III": "<:CWL_Bronze3:1390931019275964426>",
    "Bronze League II": "<:CWL_Bronze2:1390930987034349732>",
    "Bronze League I": "<:CWL_Bronze1:1390930959951593553>",
    "Silver League III": "<:CWL_Silver3:1390931121495212188>",
    "Silver League II": "<:CWL_Silver2:1390931089727557653>",
    "Silver League I": "<:CWL_Silver1:1390931056982757409>",
    "Gold League III": "<:CWL_Gold3:1390931242832367639>",
    "Gold League II": "<:CWL_Gold2:1390931211827806339>",
    "Gold League I": "<:GoldI:1234567890000000010>",
    "Crystal League III": "<:CWL_Crystal3:1390931578578010224>",
    "Crystal League II": "<:CWL_Crystal2:1390931553835810960>",
    "Crystal League I": "<:CWL_Crystal1:1390931527680135239>",
    "Master League III": "<:CWL_Master3:1390931654809489511>",
    "Master League II": "<:CWL_Master2:1390931632206381168>",
    "Master League I": "<:CWL_Master1:1390931603886178365>",
    "Champion League III": "<:CWL_Champion3:1390931733435650139>",
    "Champion League II": "<:CWL_Champion2:1390931713307185303>",
    "Champion League I": "<:CWL_Champion1:1390931693073989703>"
}

CAPITAL_LEAGUE_EMOJIS = {
    "Unranked": "<:Unranked:1390942114875179079>",
    "Bronze League III": "<:Bronze_III:1390944988648571062>",
    "Bronze League II": "<:Bronze_II:1390944540235661424>",
    "Bronze League I": "<:Bronze_I:1390944515799646278>",
    "Silver League III": "<:Silver_III:1390944489060696137>",
    "Silver League II": "<:Silver_II:1390944437911425125>",
    "Silver League I": "<:Silver_I:1390944408030937160>",
    "Gold League III": "<:Gold_III:1390944375751573575>",
    "Gold League II": "<:Gold_II:1390944347800997958>",
    "Gold League I": "<:Gold_I:1390944202392604672>",
    "Crystal League III": "<:Crystal_III:1390943009708965908>",
    "Crystal League II": "<:Crystal_II:1390942951307218994>",
    "Crystal League I": "<:Crystal_I:1390942923423744031>",
    "Master League III": "<:Master_III:1390942891584520233>",
    "Master League II": "<:Master_II:1390942868406931496>",
    "Master League I": "<:Master_I:1390942841718575155>",
    "Champion League III": "<:Champion_III:1390942814350741524>",
    "Champion League II": "<:Champion_II:1390942760340688936>",
    "Champion League I": "<:Champion_I:1390942736332623913>",
    "Titan League III": "<:Titan_III:1390942706737348608>",
    "Titan League II": "<:Titan_II:1390942680858624173>",
    "Titan League I": "<:Titan_I:1390942634905964595>",
    "Legend League": "<:Legend:1390942592060883076>"
}

WAR_LOG_EMOJIS = {
    "public": "<:Pad_Unlock:1390947990994419733>",   # Use your custom emoji if preferred
    "private": "<:Pad_Lock:1390947967443275846>",  # Use your custom emoji if preferred
}

# ---------- Clan Type Mapping ----------
CLAN_TYPE_MAP = {
    "open": "Anyone Can Join",
    "inviteOnly": "Invite Only",
    "closed": "Closed"
}

# ---------- Environment Variables ----------
COC_API_TOKEN = os.getenv("API_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- API & DB Utilities ----------
async def get_coc_clan(clan_tag):
    url = f"https://cocproxy.royaleapi.dev/v1/clans/{clan_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            return None

async def get_clan_season(clan_tag):
    # Return current month and year in MMM-YY format (e.g., Jul-25)
    return datetime.now().strftime("%b-%y")

async def get_linked_clans(guild_id):
    try:
        response = supabase.table("linked_clans").select("*").eq("guild_id", guild_id).execute()
        if response.data:
            return response.data[0]
        return {"guild_id": guild_id, "clans": []}
    except Exception as e:
        print(f"Supabase get_linked_clans error: {e}")
        return {"guild_id": guild_id, "clans": []}

# ---------- Autocomplete ----------
def setup(bot):
    async def clan_tag_autocomplete(interaction: discord.Interaction, current: str):
        data = await get_linked_clans(str(interaction.guild.id))
        clans = data.get("clans", [])
        return [
            discord.app_commands.Choice(
                name=f"{clan['name']} ({clan['tag']})",
                value=clan['tag']
            )
            for clan in clans
            if current.lower() in clan['tag'].lower() or current.lower() in clan['name'].lower()
        ][:25]

    @bot.tree.command(name="clan", description="Get clan information.")
    @discord.app_commands.describe(tag="Clan tag (e.g. #2Q82LRL)")
    @discord.app_commands.autocomplete(tag=clan_tag_autocomplete)
    async def clan_command(interaction: discord.Interaction, tag: str):
        await interaction.response.defer()
        clan_data = await get_coc_clan(tag)
        if not clan_data:
            await interaction.followup.send("No clan found for the provided tag.")
            return

        # ========== CLAN HEADER ==========
        league = clan_data.get("warLeague", {}).get("name", "Unranked")  # Keep full name, e.g., "Silver II"
        league_emoji = LEAGUE_EMOJIS.get(league, LEAGUE_EMOJIS["Unranked"])
        clan_name = clan_data.get('name', '?')
        clan_tag = clan_data.get('tag', '?')
        clan_level = clan_data.get("clanLevel", "?")
        member_count = clan_data.get("members", "?")
        trophies = clan_data.get("clanPoints", "?")

        # ========== LEADER ==========
        leader = next((m for m in clan_data.get("memberList", []) if m.get("role") == "leader"), None)
        leader_name = leader["name"] if leader else "Unknown"
        leader_tag = leader["tag"] if leader else None
        leader_link = f"https://link.clashofclans.com/en/?action=OpenPlayerProfile&tag={leader_tag[1:]}" if leader_tag else None

        # ========== LOCATION, TYPE, REQUIREMENT ==========
        location = clan_data.get("location", {}).get("name", "None")
        clan_type = CLAN_TYPE_MAP.get(clan_data.get("type", "?"), clan_data.get("type", "?"))
        required_th = clan_data.get("requiredTownhallLevel", "?")
        required_th_emoji = TH_EMOJIS.get(required_th, "")
        required_trophies = clan_data.get("requiredTrophies", "?")

        # ========== DESCRIPTION ==========
        description = clan_data.get("description", "")

        # ========== WAR LOGS ==========
        war_log_public = clan_data.get("isWarLogPublic", False)
        war_log_status = "public" if war_log_public else "private"
        war_log_emoji = WAR_LOG_EMOJIS[war_log_status]
        war_wins = clan_data.get("warWins", "?")
        war_losses = clan_data.get("warLosses", "?")
        war_ties = clan_data.get("warTies", "?")
        war_streak = clan_data.get("warWinStreak", "?")

        # ========== SEASON STATS ==========
        season = await get_clan_season(tag)  # Fetch season
        total_donated = sum([m.get("donations", 0) for m in clan_data.get("memberList", [])])
        total_received = sum([m.get("donationsReceived", 0) for m in clan_data.get("memberList", [])])

        # ========== CLAN CAPITAL ==========
        capital_league = clan_data.get("capitalLeague", {}).get("name", "Unranked")  # Keep full name, e.g., "Silver II"
        capital_league_emoji = CAPITAL_LEAGUE_EMOJIS.get(capital_league, CAPITAL_LEAGUE_EMOJIS["Unranked"])
        capital_hall = clan_data.get("clanCapital", {}).get("capitalHallLevel", "?")
        capital_hall_emoji = CAPITAL_HALL_EMOJIS.get(capital_hall, "")
        capital_points = clan_data.get("clanCapitalPoints", "?")

        # ========== TOWN HALL STATS ==========
        th_counts = {}
        for member in clan_data.get("memberList", []):
            th = member.get("townHallLevel")
            if th:
                th_counts[th] = th_counts.get(th, 0) + 1
        th_stats = []
        for th in sorted(th_counts.keys(), reverse=True):
            emoji = TH_EMOJIS.get(th, f"TH{th}")
            th_stats.append(f"{emoji} {th_counts[th]}")
        th_stats_str = " ".join(th_stats) if th_stats else "N/A"

        # ========== EMBED ==========
        embed = discord.Embed(
            title=f"{clan_name} ({clan_tag})",
            color=0xcccccc,
            description=(
                f"<:Clan:1390949992918945792> {clan_level} <:People:1390950050196226129> {member_count} <:Trophy:1390652405649248347> {trophies}\n"
                f"{league_emoji} {league}"
            )
        )
        if clan_data.get("badgeUrls", {}).get("large"):
            embed.set_thumbnail(url=clan_data["badgeUrls"]["large"])

        # Leader/location/requirements
        leader_display = f"[{leader_name}]({leader_link})" if leader_link else leader_name
        embed.add_field(
            name="",
            value=f"<:Leader:1390950209768652840> Leader: {leader_display}\n"
                  f"<:Location:1390950233562943638> Location: {location}\n"
                  f"<:Setting:1390950561095876708> Type: {clan_type}\n"
                  f"<:Clan_2:1390950727601491968> Requirement:\n"
                  f"{required_th_emoji} {required_th}+ | <:Trophy:1390652405649248347> {required_trophies}",
            inline=False
        )

        # Description
        embed.add_field(
            name="Description",
            value=description or "No description.",
            inline=False
        )

        # War logs
        if war_log_public:
            war_log_str = (
                f"{war_log_emoji} Public War Log\n"
                f"<:Check:1390952871117455442> {war_wins} Wins <:Unchecked:1390952810643853453> {war_losses} Lost <:Unchecked_2:1390952837197991936> {war_ties} Draw\n"
                f"<:Chart:1391842349482508369> Win Streak: {war_streak}\n"
            )
        else:
            war_log_str = f"{war_log_emoji} Private War Log"
        embed.add_field(
            name="War Logs",
            value=war_log_str,
            inline=False
        )

        # Calculate active players
        active_players = [
            m for m in clan_data.get("memberList", [])
            if m.get("donations", 0) > 0 or m.get("donationsReceived", 0) > 0
        ]
        active_count = len(active_players)

        # Season stats
        embed.add_field(
            name=f"Season Stats ({season})",
            value=f"<:Arrow_Right:1390721523765088447> Donated: {total_donated}\n"
                  f"<:Arrow_Left:1390721571508977858> Received: {total_received}\n"
                  f"<:Chart_2:1390954429116579840> Active Players: ~{active_count}/day",
            inline=False
        )

        # Clan Capital
        embed.add_field(
            name="Clan Capital",
            value=f"{capital_league_emoji} {capital_league}\n"
                  f"{capital_hall_emoji} Capital Hall: {capital_hall}\n"
                  f"<:Capital_Point:1390954582166863986> Capital Points: {capital_points}",
            inline=False
        )

        # Town Hall Stats
        embed.add_field(
            name="Town Hall Stats",
            value=th_stats_str,
            inline=False
        )

        # ========== BUTTON ==========
        class ClanButtonView(discord.ui.View):
            def __init__(self, coc_url, badge_url):
                super().__init__()
                # Add Clan Badge button first
                if badge_url:
                    self.add_item(discord.ui.Button(
                        label="Clan Badge",
                        url=badge_url,
                        style=discord.ButtonStyle.link
                    ))
                # Add Open In-game button
                self.add_item(discord.ui.Button(
                    label="Open In-game",
                    url=coc_url,
                    style=discord.ButtonStyle.link
                ))

        coc_url = f"https://link.clashofclans.com/en?action=OpenClanProfile&tag={clan_tag[1:]}" if clan_tag.startswith("#") else clan_tag
        badge_url = clan_data.get("badgeUrls", {}).get("large")

        await interaction.followup.send(embed=embed, view=ClanButtonView(coc_url, badge_url))
        
        coc_url = f"https://link.clashofclans.com/en?action=OpenClanProfile&tag={clan_tag[1:]}" if clan_tag.startswith("#") else clan_tag

        await interaction.followup.send(embed=embed, view=OpenIngameButton(coc_url))