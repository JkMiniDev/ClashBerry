import os
import discord
import aiohttp
from supabase import acreate_client, AsyncClient
import datetime

COC_API_TOKEN = os.getenv("API_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: AsyncClient = None

TH_EMOJIS = {
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
def th_emoji(level):
    return TH_EMOJIS.get(int(level), "")

async def init_supabase_client():
    global supabase
    if supabase is None:
        try:
            supabase = await acreate_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")

async def fetch_json(url, headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 403:
                data = await resp.json()
                if data.get("reason") == "accessDenied":
                    return {"error": "accessDenied"}
            return None

async def get_coc_clan_war(clan_tag):
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    tag = clan_tag.replace("#", "%23")

    # Try current war (normal or cwl)
    url = f"https://cocproxy.royaleapi.dev/v1/clans/{tag}/currentwar"
    data = await fetch_json(url, headers)
    if data:
        if data.get("error") == "accessDenied":
            return data, "accessDenied"
        if data.get("state") not in (None, "notInWar"):
            return data, "normal"

    # Try CWL group and always prefer "inWar" round if present
    cwl_url = f"https://cocproxy.royaleapi.dev/v1/clans/{tag}/currentwar/leaguegroup"
    cwl_data = await fetch_json(cwl_url, headers)
    if cwl_data and "rounds" in cwl_data and "clans" in cwl_data:
        clean_clan_tag = clan_tag.replace("%23", "#")
        all_war_objs = []
        for idx, rnd in enumerate(reversed(cwl_data["rounds"])):
            current_round_num = len(cwl_data["rounds"]) - idx
            if "warTags" in rnd:
                for war_tag_in_round in rnd["warTags"]:
                    if war_tag_in_round and war_tag_in_round != "#0":
                        war_url = f"https://cocproxy.royaleapi.dev/v1/clanwarleagues/wars/{war_tag_in_round.replace('#', '%23')}"
                        war = await fetch_json(war_url, headers)
                        if war and war.get("clan") and war.get("opponent"):
                            our_clan_data = None
                            opponent_clan_data = None
                            if war["clan"]["tag"].lower() == clean_clan_tag.lower():
                                our_clan_data = war["clan"]
                                opponent_clan_data = war["opponent"]
                            elif war["opponent"]["tag"].lower() == clean_clan_tag.lower():
                                our_clan_data = war["opponent"]
                                opponent_clan_data = war["clan"]
                            if our_clan_data:
                                war_for_embed = {
                                    "state": war["state"],
                                    "teamSize": war.get("teamSize"),
                                    "preparationStartTime": war.get("preparationStartTime"),
                                    "startTime": war.get("startTime"),
                                    "endTime": war.get("endTime"),
                                    "clan": our_clan_data,
                                    "opponent": opponent_clan_data,
                                    "cwl_round": current_round_num,
                                    "type": "cwl"
                                }
                                all_war_objs.append(war_for_embed)
        
        # Prefer inWar > preparation first
        for state in ("inWar", "preparation"):
            for war in all_war_objs:
                if war["state"] == state:
                    return war, "cwl"
        
        # Check for ended CWL wars within 24 hours
        now = datetime.datetime.utcnow()
        ended_wars = [war for war in all_war_objs if war["state"] == "warEnded"]
        
        for war in ended_wars:
            end_time_iso = war.get("endTime")
            if end_time_iso:
                try:
                    end_time_dt = datetime.datetime.strptime(end_time_iso, "%Y%m%dT%H%M%S.000Z")
                    hours_since_end = (now - end_time_dt).total_seconds() / 3600
                    if hours_since_end <= 24:  # Show only if ended within 24 hours
                        return war, "cwl"
                except Exception:
                    continue

    # If no current war and no cwl, return not in war
    return None, "notInWar"

async def get_linked_clans(guild_id):
    await init_supabase_client()
    if supabase is None:
        return {"guild_id": guild_id, "clans": []}
    try:
        response = await supabase.table("linked_clans").select("*").eq("guild_id", guild_id).execute()
        if response.data:
            return response.data[0]
        return {"guild_id": guild_id, "clans": []}
    except Exception as e:
        print(f"Supabase get_linked_clans error: {e}")
        return {"guild_id": guild_id, "clans": []}

def _star_string(stars: int):
    if stars == 3:
        return "★★★"
    elif stars == 2:
        return "★★☆"
    elif stars == 1:
        return "★☆☆"
    else:
        return "☆☆☆"

EMBED_COLOR = discord.Color(int("0xcccccc", 16))

def make_attacks_embed(war_data, war_type):
    clan = war_data.get("clan", {})
    members = sorted(clan.get("members", []), key=lambda m: int(m.get("townhallLevel", 1)), reverse=True)
    attacks_expected = 1 if war_type == "cwl" else 2
    total_attacks = len(members) * attacks_expected
    done_attacks = sum(len(m.get("attacks", [])) for m in members)

    # Main attacks header
    header = f"**Attacks {done_attacks}/{total_attacks}**"
    lines = []
    for m in members:
        th_icon = th_emoji(m.get("townhallLevel", "?"))
        for atk in sorted(m.get("attacks", []), key=lambda a: -a.get("order", 0)):
            stars = _star_string(atk.get("stars", 0))
            percent = atk.get("destructionPercentage", 0)
            lines.append(f"{th_icon} {m['name']} ({m['tag']}) - {stars} {percent}%")

    if not lines:
        lines.append("No attacks recorded yet.")

    # Add remaining attacks section if war is in progress
    if war_data.get("state") == "inWar":
        remaining_lines = []
        for m in members:
            attacks_done = len(m.get("attacks", []))
            if attacks_done < attacks_expected:
                th_icon = th_emoji(m.get("townhallLevel", "?"))
                remaining_lines.append(f"{th_icon} {m['name']} ({m['tag']}) - {attacks_done}/{attacks_expected}")

        if remaining_lines:
            lines.append("")  # Empty line for separation
            lines.append("**Remaining Attacks**")
            lines.extend(remaining_lines)
        else:
            lines.append("")
            lines.append("**Remaining Attacks**")
            lines.append("All attacks have been used!")

    # Add missed attacks section if CWL war ended
    if war_data.get("state") == "warEnded" and war_type == "cwl":
        missed_lines = []
        for m in members:
            attacks_done = len(m.get("attacks", []))
            if attacks_done < attacks_expected:
                th_icon = th_emoji(m.get("townhallLevel", "?"))
                missed_lines.append(f"{th_icon} {m['name']} ({m['tag']}) - {attacks_done}/{attacks_expected}")

        if missed_lines:
            lines.append("")  # Empty line for separation
            lines.append("**Missed Attacks**")
            lines.extend(missed_lines)
        else:
            lines.append("")
            lines.append("**Missed Attacks**")
            lines.append("No missed attacks!")

    embed = discord.Embed(
        description='\n'.join([header] + lines[:100]),  # Increased limit to accommodate additional sections
        color=EMBED_COLOR
    )
    embed.set_author(name=f"{clan.get('name')} ({clan.get('tag')})", icon_url=clan.get("badgeUrls", {}).get("large", ""))
    if war_type == "cwl":
        embed.set_footer(text=f"CWL - #Round {war_data.get('cwl_round', '?')}")
    return embed

def make_defences_embed(war_data, war_type):
    clan = war_data.get("clan", {})
    opponent = war_data.get("opponent", {})
    members = sorted(clan.get("members", []), key=lambda m: int(m.get("townhallLevel", 1)), reverse=True)
    attacks_expected = 1 if war_type == "cwl" else 2
    total_attacks = len(members) * attacks_expected
    all_players = {m["tag"]: m for m in clan.get("members", []) + opponent.get("members", [])}
    defences = []
    for opp_member in opponent.get("members", []):
        for atk in opp_member.get("attacks", []):
            defender_tag = atk.get("defenderTag")
            if defender_tag in all_players and defender_tag in [m["tag"] for m in members]:
                defender = all_players[defender_tag]
                th_icon = th_emoji(defender.get("townhallLevel", "?"))
                stars = _star_string(atk.get("stars", 0))
                percent = atk.get("destructionPercentage", 0)
                defences.append({
                    "th": th_icon,
                    "name": defender["name"],
                    "tag": defender["tag"],
                    "stars": stars,
                    "percent": percent,
                    "order": atk.get("order", 0)
                })
    defences.sort(key=lambda d: -d["order"])
    header = f"**Defence {len(defences)}/{total_attacks}**"
    lines = [f"{d['th']} {d['name']} ({d['tag']}) - {d['stars']} {d['percent']}%" for d in defences]
    if not lines:
        lines.append("No defences recorded yet.")
    embed = discord.Embed(
        description='\n'.join([header] + lines[:45]),
        color=EMBED_COLOR
    )
    embed.set_author(name=f"{clan.get('name')} ({clan.get('tag')})", icon_url=clan.get("badgeUrls", {}).get("large", ""))
    if war_type == "cwl":
        embed.set_footer(text=f"CWL - #Round {war_data.get('cwl_round', '?')}")
    return embed

def make_clan_roster_embed(war_data, war_type):
    clan = war_data.get("clan", {})
    members = sorted(clan.get("members", []), key=lambda m: int(m.get("townhallLevel", 1)), reverse=True)
    header = "**<:People:1390950050196226129> Clan Roster**"
    lines = [f"{th_emoji(m.get('townhallLevel', '?'))} {m['name']} ({m['tag']})" for m in members]
    if not lines:
        lines.append("No members listed.")
    embed = discord.Embed(
        description='\n'.join([header] + lines),
        color=EMBED_COLOR
    )
    embed.set_author(name=f"{clan.get('name')} ({clan.get('tag')})", icon_url=clan.get("badgeUrls", {}).get("large", ""))
    if war_type == "cwl":
        embed.set_footer(text=f"CWL - #Round {war_data.get('cwl_round', '?')}")
    return embed

def make_opponent_roster_embed(war_data, war_type):
    opponent = war_data.get("opponent", {})
    members = sorted(opponent.get("members", []), key=lambda m: int(m.get("townhallLevel", 1)), reverse=True)
    header = "**<:People:1390950050196226129> Opponent Roster**"
    lines = [f"{th_emoji(m.get('townhallLevel', '?'))} {m['name']} ({m['tag']})" for m in members]
    if not lines:
        lines.append("No members listed.")
    embed = discord.Embed(
        description='\n'.join([header] + lines),
        color=EMBED_COLOR
    )
    embed.set_author(name=f"{opponent.get('name')} ({opponent.get('tag')})", icon_url=opponent.get("badgeUrls", {}).get("large", ""))
    if war_type == "cwl":
        embed.set_footer(text=f"CWL - #Round {war_data.get('cwl_round', '?')}")
    return embed

def make_overview_embed(war_data, war_type):
    clan = war_data.get("clan", {})
    opponent = war_data.get("opponent", {})
    team_size = war_data.get("teamSize", 0)
    embed = discord.Embed(
        title=f"{clan.get('name')} ({clan.get('tag')})",
        color=EMBED_COLOR
    )
    embed.set_thumbnail(url=clan.get("badgeUrls", {}).get("large", ""))
    desc = []
    desc.append(f"**Opponent Clan**\n{opponent.get('name', '?')} ({opponent.get('tag', '?')})")
    desc.append(f"**Team Size**\n{team_size} vs {team_size}")
    now = datetime.datetime.utcnow()
    status = war_data.get("state", "-")
    if status == "inWar":
        ending = "-"
        end_time_iso = war_data.get("endTime")
        if end_time_iso:
            try:
                end_time_dt = datetime.datetime.strptime(end_time_iso, "%Y%m%dT%H%M%S.000Z")
                remaining = end_time_dt - now
                hours = max(0, int(remaining.total_seconds() // 3600))
                ending = f"`{hours} Hrs`"
            except Exception: pass
        desc.append(f"**War Status**\n<a:Battle:1391864971981357216> Battle Day\n<:Time:1391862881217151127> Ending in: {ending}")
    elif status == "warEnded":
        ended = "-"
        end_time_iso = war_data.get("endTime")
        if end_time_iso:
            try:
                end_time_dt = datetime.datetime.strptime(end_time_iso, "%Y%m%dT%H%M%S.000Z")
                ago = now - end_time_dt
                total_seconds = ago.total_seconds()
                if total_seconds >= 86400:  # 24 hours
                    days = int(total_seconds // 86400)
                    ended = f"`{days} Day` ago" if days == 1 else f"`{days} Days` ago"
                else:
                    hours = max(0, int(total_seconds // 3600))
                    ended = f"`{hours} Hrs` ago"
            except Exception: pass
        desc.append(f"**War Status**\n<:Clock:1391864123188576326> War Ended\n<:Time:1391862881217151127> Ended: {ended}")
    elif status == "preparation":
        start = "-"
        start_time_iso = war_data.get("startTime")
        if start_time_iso:
            try:
                start_time_dt = datetime.datetime.strptime(start_time_iso, "%Y%m%dT%H%M%S.000Z")
                left = start_time_dt - now
                hours = max(0, int(left.total_seconds() // 3600))
                start = f"`{hours} Hrs`"
            except Exception: pass
        desc.append(f"**War Status**\n<:Clock:1391864123188576326> Preparation Day\n<:Time:1391862881217151127> Starting in: {start}")
    attacks_expected = 1 if war_type == "cwl" else 2
    desc.append("**Summary**")
    desc.append(f"**{clan.get('name', '?')}**\n<:Sword:1390659453321351289> Attacks: {clan.get('attacks', 0)}/{team_size*attacks_expected}\n<:Star_1:1391862120706212041> Earned Stars: {clan.get('stars', 0)}/{team_size*3}\n<:Broken_sword:1391860640880267415> Destruction: {float(clan.get('destructionPercentage', 0)):.2f}%")
    desc.append(f"**{opponent.get('name', '?')}**\n<:Sword:1390659453321351289> Attacks: {opponent.get('attacks', 0)}/{team_size*attacks_expected}\n<:Star_1:1391862120706212041> Earned Stars: {opponent.get('stars', 0)}/{team_size*3}\n<:Broken_sword:1391860640880267415> Destruction: {float(opponent.get('destructionPercentage', 0)):.2f}%")
    desc.append("**Composition**")
    def th_breakdown(members):
        th_counts = {}
        for m in members:
            lvl = int(m.get("townhallLevel", 0))
            th_counts[lvl] = th_counts.get(lvl, 0) + 1
        sorted_ths = sorted(th_counts.items(), reverse=True)
        return ' '.join(f"{TH_EMOJIS.get(th, '')} `{count}`" for th, count in sorted_ths)
    desc.append(f"{clan.get('name', '?')}\n{th_breakdown(clan.get('members', []))}")
    desc.append(f"{opponent.get('name', '?')}\n{th_breakdown(opponent.get('members', []))}")
    embed.description = '\n\n'.join(desc)
    if war_type == "cwl":
        embed.set_footer(text=f"CWL - #Round {war_data.get('cwl_round', '?')}")
    return embed

async def make_private_war_log_embed(clan_tag):
    embed = discord.Embed(
        description="Private War Log",
        color=EMBED_COLOR
    )

    # Fetch clan info to get name and badge
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    tag = clan_tag.replace("#", "%23")
    url = f"https://cocproxy.royaleapi.dev/v1/clans/{tag}"
    clan_data = await fetch_json(url, headers)

    if clan_data and "name" in clan_data:
        embed.set_author(name=f"{clan_data['name']} ({clan_data['tag']})", icon_url=clan_data.get("badgeUrls", {}).get("large", ""))
    else:
        embed.set_author(name=f"Clan ({clan_tag})")

    return embed

async def make_not_in_war_embed(clan_tag):
    embed = discord.Embed(
        description="Not in war",
        color=EMBED_COLOR
    )

    # Fetch clan info to get name and badge
    headers = {"Authorization": f"Bearer {COC_API_TOKEN}"}
    tag = clan_tag.replace("#", "%23")
    url = f"https://cocproxy.royaleapi.dev/v1/clans/{tag}"
    clan_data = await fetch_json(url, headers)

    if clan_data and "name" in clan_data:
        embed.set_author(name=f"{clan_data['name']} ({clan_data['tag']})", icon_url=clan_data.get("badgeUrls", {}).get("large", ""))
    else:
        embed.set_author(name=f"Clan ({clan_tag})")

    return embed

class WarView(discord.ui.View):
    def __init__(self, war_data, war_type, current="overview"):
        super().__init__(timeout=300)
        self.add_item(WarDropdown(war_data, war_type, current))

class WarDropdown(discord.ui.Select):
    def __init__(self, war_data, war_type, current):
        options = [
            discord.SelectOption(
                label="Overview",
                description="Show war summary",
                value="overview",
                emoji="<:Clan_war:1391859721589493913>",
                default=(current=="overview")
            ),
        ]
        war_state = war_data.get("state")
        if war_state == "preparation":
            options.append(discord.SelectOption(
                label="Clan Roster",
                description="List members",
                value="clan_roster",
                emoji="<:People:1390950050196226129>",
                default=(current=="clan_roster")
            ))
            options.append(discord.SelectOption(
                label="Opponent Roster",
                description="List opponent members",
                value="opponent_roster",
                emoji="<:People:1390950050196226129>",
                default=(current=="opponent_roster")
            ))
        else:
            options.append(discord.SelectOption(
                label="Attacks",
                description="Show attacks",
                value="attacks",
                emoji="<:Sword:1390659453321351289>",
                default=(current=="attacks")
            ))
            options.append(discord.SelectOption(
                label="Defence",
                description="Show defences",
                value="defence",
                emoji="<:Broken_sword:1391860640880267415>",
                default=(current=="defence")
            ))
        super().__init__(placeholder="Select info to view...", min_values=1, max_values=1, options=options)
        self.war_data = war_data
        self.war_type = war_type

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        if value == "overview":
            embed = make_overview_embed(self.war_data, self.war_type)
        elif value == "attacks":
            embed = make_attacks_embed(self.war_data, self.war_type)
        elif value == "defence":
            embed = make_defences_embed(self.war_data, self.war_type)
        elif value == "clan_roster":
            embed = make_clan_roster_embed(self.war_data, self.war_type)
        elif value == "opponent_roster":
            embed = make_opponent_roster_embed(self.war_data, self.war_type)
        else:
            embed = discord.Embed(title="Invalid selection.")
        view = WarView(self.war_data, self.war_type, current=value)
        await interaction.response.edit_message(embed=embed, view=view)
