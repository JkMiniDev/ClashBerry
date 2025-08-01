import os
import discord
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
import json  # Added for max_lvl.json and emoji loading

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# Initialize MongoDB client
mongodb_client = AsyncIOMotorClient(MONGODB_URI)
db = mongodb_client[MONGODB_DATABASE]

# Load max_lvl.json using absolute path
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    max_json_path = os.path.join(script_dir, 'config', 'max_lvl.json')
    with open(max_json_path, 'r') as f:
        max_levels = json.load(f)
except FileNotFoundError:
    print(f"Error: 'max_lvl.json' not found at {max_json_path}")
    max_levels = {}
except Exception as e:
    print(f"Error loading max_lvl.json: {str(e)}")
    max_levels = {}

class PlayerEmbeds:
    ELIXIR_TROOPS = [
        "Barbarian", "Archer", "Giant", "Goblin", "Wall Breaker", "Balloon", "Wizard",
        "Healer", "Dragon", "P.E.K.K.A", "Baby Dragon", "Miner", "Electro Dragon", "Yeti", "Dragon Rider",
        "Electro Titan", "Root Rider", "Thrower"
    ]
    DARK_TROOPS = [
        "Minion", "Hog Rider", "Valkyrie", "Golem", "Witch", "Lava Hound", "Bowler",
        "Ice Golem", "Headhunter", "Apprentice Warden", "Druid", "Furnace"
    ]
    PETS = [
        "L.A.S.S.I", "Electro Owl", "Mighty Yak", "Unicorn", "Frosty", "Diggy", "Poison Lizard",
        "Phoenix", "Spirit Fox", "Angry Jelly", "Sneezy"
    ]
    ELIXIR_SPELLS = [
        "Lightning Spell", "Healing Spell", "Rage Spell", "Jump Spell", "Freeze Spell", "Clone Spell",
        "Invisibility Spell", "Recall Spell", "Revive Spell"
    ]
    DARK_SPELLS = [
        "Poison Spell", "Earthquake Spell", "Haste Spell", "Skeleton Spell", "Bat Spell",
        "Overgrowth Spell", "Ice Block Spell"
    ]
    SIEGE_MACHINES = [
        "Wall Wrecker", "Battle Blimp", "Stone Slammer", "Siege Barracks", "Log Launcher",
        "Flame Flinger", "Battle Drill", "Troop Launcher"
    ]
    HEROES = [
        "Barbarian King", "Archer Queen", "Grand Warden", "Royal Champion", "Minion Prince"
    ]
    HERO_EQUIPMENT_NAMES = [
        "Giant Gauntlet", "Rocket Spear", "Spiky Ball", "Frozen Arrow", "Fireball",
        "Snake Bracelet", "Dark Crown", "Magic Mirror", "Electro Boots", "Action Figure",
        "Barbarian Puppet", "Rage Vial", "Archer Puppet", "Invisibility Vial", "Eternal Tome",
        "Life Gem", "Seeking Shield", "Royal Gem", "Earthquake Boots", "Hog Rider Puppet",
        "Haste Vial", "Giant Arrow", "Healer Puppet", "Rage Gem", "Healing Tome",
        "Henchmen Puppet", "Dark Orb", "Metal Pants", "Vampstache", "Noble Iron"
    ]

    # Load emoji mappings from JSON files
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(script_dir, 'commands', 'emoji', 'town_halls.json'), 'r') as f:
        TH_EMOJIS = json.load(f)
    with open(os.path.join(script_dir, 'commands', 'emoji', 'home_units.json'), 'r') as f:
        UNIT_EMOJIS = json.load(f)
    
    # Combine all emojis into one map for compatibility
    EMOJI_MAP = {**UNIT_EMOJIS}
    for th_level, emoji in TH_EMOJIS.items():
        EMOJI_MAP[f"TH{th_level}"] = emoji
# Profile Info
    @staticmethod
    def format_number(number):
        """Convert a number to abbreviated format (e.g., 2000 -> 2K, 2200000 -> 2.2M, 1500000000 -> 1.5B)."""
        if number < 1000:
            return str(number)
        elif number < 1000000:
            return f"{number / 1000:.1f}K".rstrip('0').rstrip('.')
        elif number < 1000000000:
            return f"{number / 1000000:.1f}M".rstrip('0').rstrip('.')
        else:
            return f"{number / 1000000000:.1f}B".rstrip('0').rstrip('.')

    @staticmethod
    def player_info(player_data):
        player_tag = player_data.get('tag', '')
        player_name = player_data.get('name', '?')
        
        # Create clickable title URL
        title_url = None
        if player_tag and player_tag.startswith('#'):
            tag_clean = player_tag[1:]
            title_url = f"https://link.clashofclans.com/?action=OpenPlayerProfile&tag=%23{tag_clean}"
        
        embed = discord.Embed(
            title=f"{player_name} ({player_tag})",
            url=title_url,
            color=0xcccccc
        )

        # Description: Town Hall with emoji, Exp, and Trophies in one line
        th_level = player_data.get('townHallLevel', '?')
        exp_level = player_data.get('expLevel', '?')
        trophies = player_data.get('trophies', '?')
        th_emoji = PlayerEmbeds.EMOJI_MAP.get(f"TH{th_level}", f"TH{th_level}")
        try:
            embed.description = f"{th_emoji} {th_level} <:EXP:1390652382693556324> {exp_level} <:Trophy:1390652405649248347> {trophies}"
        except Exception as e:
            print(f"Error setting embed description: {str(e)}")
            embed.description = f"TH{th_level} Exp: {exp_level} Trophies: {trophies}"

        # Clan: Name (clickable link) - Role
        clan = player_data.get("clan", {})
        clan_name = clan.get("name", "None")
        role_raw = player_data.get("role", "notInClan")
        role_map = {
            "admin": "Elder",
            "coLeader": "Co-Leader",
            "leader": "Leader",
            "member": "Member",
            "notInClan": "Not In Clan"
        }
        clan_role = role_map.get(role_raw, "Unknown")
        if clan_name != "None" and clan.get("tag"):
            clan_tag = clan["tag"].replace("#", "")
            clan_url = f"https://link.clashofclans.com/?action=OpenClanProfile&tag=%23{clan_tag}"
            clan_display = f"[{clan_name}]({clan_url})"
            embed.add_field(name="Clan", value=f"{clan_display} - {clan_role}", inline=False)
        else:
            embed.add_field(name="Clan", value="Not In Clan", inline=False)

        # Season Stats
        season_stats = (
            f"<:Arrow_Right:1390721523765088447> Donated: {player_data.get('donations', 0)}\n"
            f"<:Arrow_Left:1390721571508977858> Received: {player_data.get('donationsReceived', 0)}\n"
            f"<:Sword:1390659453321351289> Attack Wins: {player_data.get('attackWins', 0)}\n"
            f"<:Shield:1390659485273423914> Defense Wins: {player_data.get('defenseWins', 0)}"
        )
        embed.add_field(name="Season Stats", value=season_stats, inline=False)

        # New War Stats field
        achievements = {a["name"]: a["value"] for a in player_data.get("achievements", [])}
        war_preference_raw = player_data.get("warPreference")
        war_preference = war_preference_raw.capitalize() if war_preference_raw else ""
        war_lines = [
            f"<:Star_1:1391862120706212041> War Stars: {player_data.get('warStars', '?')}",
            f"<:Star:1390656503987568651> CWL Stars: {achievements.get('War League Legend', 0)}"
        ]
        if war_preference == "In":
            war_lines.append(f"<:Opt_in:1395090219711070370> Preference: In")
        elif war_preference == "Out":
            war_lines.append(f"<:Opt_out:1395090188643860560> Preference: Out")
        war_stats = "\n".join(war_lines)
        embed.add_field(name="War Stats", value=war_stats, inline=False)

        # Overall Stats (remaining achievements)
        overall_stats = (
            f"<:Gold:1390666299054755950> Total Loot: <:Gold:1390666299054755950> {PlayerEmbeds.format_number(achievements.get('Gold Grab', 0))} <:Elixir:1390666277856608306> {PlayerEmbeds.format_number(achievements.get('Elixir Escapade', 0))} <:Dark_Elixir:1390666254670630912> {PlayerEmbeds.format_number(achievements.get('Heroic Heist', 0))}\n"
            f"<:Trophy:1390652405649248347> Best Trophy: {player_data.get('bestTrophies', '?')}\n"
            f"<:Sword:1390659453321351289> Attack Wins: {achievements.get('Conqueror', 0)}\n"
            f"<:Shield:1390659485273423914> Defense Wins: {achievements.get('Unbreakable', 0)}\n"
            f"<:Troops_Donation:1390659367241781279> Troops Donated: {achievements.get('Friend in Need', 0)}\n"
            f"<:Spell_Donation:1390659413613744228> Spells Donated: {achievements.get('Sharing is caring', 0)}\n"
            f"<:Siege_Donation:1390659389786030232> Siege Donated: {achievements.get('Siege Sharer', 0)}\n"
            f"<:Clan_games:1390660765509488774> Clan Games: {achievements.get('Games Champion', 0)}\n"
            f"<:Capital_Gold:1390661279697338420> Capital Looted: {achievements.get('Aggressive Capitalism', 0)}\n"
            f"<:Capital_Gold:1390661279697338420> Capital Donated: {achievements.get('Most Valuable Clanmate', 0)}"
        )
        embed.add_field(name="Overall Stats", value=overall_stats, inline=False)

        # Discord field - will be set by the calling function
        discord_value = player_data.get("discord_info", "Not Linked")
        embed.add_field(name="Discord", value=discord_value, inline=False)

        # League icon (if available)
        icon = player_data.get("league", {}).get("iconUrls", {}).get("medium")
        if icon:
            embed.set_thumbnail(url=icon)
        else:
            embed.set_thumbnail(url="https://i.imghippo.com/files/aYq7201ZC.png")
        return embed

    @staticmethod
    def unit_embed(player_data):
        troops = player_data.get("troops", [])
        spells = player_data.get("spells", [])
        heroes = player_data.get("heroes", [])
        hero_equipment = player_data.get("heroEquipment", [])
        th_level = str(player_data.get("townHallLevel", 1))  # Get TH level, default to 1 if missing

        def format_level(level, max_level):
            """Format level with spaces based on digit count"""
            level_str = str(level)
            max_str = str(max_level)
            # Add space before if level is single digit
            prefix = " " if len(level_str) == 1 else ""
            # Add space after if max is single digit
            suffix = " " if len(max_str) == 1 else ""
            return f"`{prefix}{level_str}/{max_str}{suffix}`"

        def troop_lines(names):
            units = [t for t in troops if t.get("name") in names and max_levels.get(t.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(t.get('name'), '❓')} {format_level(t['level'], max_levels.get(t.get('name'), {}).get(th_level, 0))}"
                        for t in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def spell_lines(names):
            units = [s for s in spells if s.get("name") in names and max_levels.get(s.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(s.get('name'), '❓')} {format_level(s['level'], max_levels.get(s.get('name'), {}).get(th_level, 0))}"
                        for s in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def pet_lines():
            units = [t for t in troops if t.get("name") in PlayerEmbeds.PETS and max_levels.get(t.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(t.get('name'), '❓')} {format_level(t['level'], max_levels.get(t.get('name'), {}).get(th_level, 0))}"
                        for t in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def siege_lines():
            units = [t for t in troops if t.get("name") in PlayerEmbeds.SIEGE_MACHINES and max_levels.get(t.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(t.get('name'), '❓')} {format_level(t['level'], max_levels.get(t.get('name'), {}).get(th_level, 0))}"
                        for t in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def hero_lines():
            units = [h for h in heroes if h.get("name") in PlayerEmbeds.HEROES and max_levels.get(h.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(h.get('name'), '❓')} {format_level(h['level'], max_levels.get(h.get('name'), {}).get(th_level, 0))}"
                        for h in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result

        def equipment_lines():
            units = [eq for eq in hero_equipment if eq.get("name") in PlayerEmbeds.HERO_EQUIPMENT_NAMES and max_levels.get(eq.get("name"), {}).get(th_level, 0) > 0]
            if not units:
                return ["None"]
            result = []
            for i in range(0, len(units), 20):  # Process in chunks of 20
                group = units[i:i + 20]
                lines = []
                for j in range(0, len(group), 4):  # 4 units per line
                    sub_group = group[j:j + 4]
                    line = " ".join(
                        f"{PlayerEmbeds.EMOJI_MAP.get(eq.get('name'), '❓')} {format_level(eq.get('level', '?'), max_levels.get(eq.get('name'), {}).get(th_level, 0))}"
                        for eq in sub_group
                    )
                    lines.append(line)
                result.append("\n".join(lines))
            return result if result else ["None"]

        embed = discord.Embed(
            title="Army Overview",
            color=0xcccccc
        )
        elixir_troops_value = troop_lines(PlayerEmbeds.ELIXIR_TROOPS)
        if elixir_troops_value[0] != "None":
            embed.add_field(name="Elixir Troops", value=elixir_troops_value[0], inline=False)
            for extra_value in elixir_troops_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        dark_troops_value = troop_lines(PlayerEmbeds.DARK_TROOPS)
        if dark_troops_value[0] != "None":
            embed.add_field(name="Dark Troops", value=dark_troops_value[0], inline=False)
            for extra_value in dark_troops_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        elixir_spells_value = spell_lines(PlayerEmbeds.ELIXIR_SPELLS)
        if elixir_spells_value[0] != "None":
            embed.add_field(name="Elixir Spells", value=elixir_spells_value[0], inline=False)
            for extra_value in elixir_spells_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        dark_spells_value = spell_lines(PlayerEmbeds.DARK_SPELLS)
        if dark_spells_value[0] != "None":
            embed.add_field(name="Dark Spells", value=dark_spells_value[0], inline=False)
            for extra_value in dark_spells_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        siege_machines_value = siege_lines()
        if siege_machines_value[0] != "None":
            embed.add_field(name="Siege Machines", value=siege_machines_value[0], inline=False)
            for extra_value in siege_machines_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        heroes_value = hero_lines()
        if heroes_value[0] != "None":
            embed.add_field(name="Heroes", value=heroes_value[0], inline=False)
            for extra_value in heroes_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        pets_value = pet_lines()
        if pets_value[0] != "None":
            embed.add_field(name="Pets", value=pets_value[0], inline=False)
            for extra_value in pets_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        equipment_value = equipment_lines()
        if equipment_value[0] != "None":
            embed.add_field(name="Hero Equipment", value=equipment_value[0], inline=False)
            for extra_value in equipment_value[1:]:
                embed.add_field(name="\u200b", value=extra_value, inline=False)
        return embed

class ViewSelector(discord.ui.Select):
    def __init__(self, player_data, current_view):
        self.player_data = player_data
        options = [
            discord.SelectOption(
                label="Profile Overview",
                description="Show player profile information",
                emoji="<:EXP:1390652382693556324>",
                default=(current_view == "Profile Overview")
            ),
            discord.SelectOption(
                label="Army Overview",
                description="Show troops, spells, and heroes",
                emoji="<:Troops:1395132747043049544>",
                default=(current_view == "Army Overview")
            )
        ]
        super().__init__(
            placeholder="Select a view...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            # Defer the interaction immediately
            await interaction.response.defer()
            
            if self.values[0] == "Profile Overview":
                embed = PlayerEmbeds.player_info(self.player_data)
            else:
                embed = PlayerEmbeds.unit_embed(self.player_data)
            
            # Check if parent view has user_accounts (multi-account view)
            if hasattr(self.view, 'user_accounts') and self.view.user_accounts:
                view = UserProfileButtonView(self.player_data, self.view.user_accounts, current_view=self.values[0])
            else:
                view = ProfileButtonView(self.player_data, current_view=self.values[0])
            
            await interaction.edit_original_response(embed=embed, view=view)
        except discord.NotFound:
            # Interaction already handled, ignore
            pass
        except Exception as e:
            print(f"Error in ViewSelector callback: {e}")

class ProfileButtonView(discord.ui.View):
    def __init__(self, player_data, current_view="Profile Overview"):
        super().__init__(timeout=None)
        self.player_data = player_data
        self.player_tag = player_data.get("tag", "")
        self.current_view = current_view

        # Add buttons first (row 0)
        self.refresh_btn = discord.ui.Button(
            emoji="🔃",
            style=discord.ButtonStyle.secondary,
            custom_id="refresh_btn",
            row=0
        )
        self.refresh_btn.callback = self.refresh_btn_callback
        self.add_item(self.refresh_btn)

        if self.player_tag:
            tag = self.player_tag.replace("#", "")
            url = f"https://link.clashofclans.com/?action=OpenPlayerProfile&tag=%23{tag}"
            self.add_item(discord.ui.Button(
                label="Open In-game",
                url=url,
                style=discord.ButtonStyle.link,
                row=0
            ))

        # Add view selector dropdown below buttons (row 1)
        view_selector = ViewSelector(player_data, current_view)
        view_selector.row = 1
        self.add_item(view_selector)

    async def refresh_btn_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            fresh_data = await get_coc_player(self.player_tag)
            if not fresh_data:
                await interaction.followup.send("⚠️ Interaction expired. Please run the command again.", ephemeral=True)
                return
            
            # Check for name changes and update database if needed
            player_tag = fresh_data.get("tag", "")
            player_name = fresh_data.get("name", "")
            if player_tag and player_name:
                await update_player_name_if_changed(player_tag, player_name)
            
            # Get Discord info for the refreshed player data
            discord_info = await get_discord_info_for_player(player_tag)
            fresh_data["discord_info"] = discord_info
            
            new_view = ProfileButtonView(fresh_data, current_view=self.current_view)
            if self.current_view == "Profile Overview":
                embed = PlayerEmbeds.player_info(fresh_data)
            else:
                embed = PlayerEmbeds.unit_embed(fresh_data)
            
            await interaction.edit_original_response(embed=embed, view=new_view)
        except discord.NotFound:
            pass
        except Exception as e:
            print(f"Error in refresh callback: {e}")
            try:
                await interaction.followup.send("❌ Failed to refresh data.", ephemeral=True)
            except:
                pass

class UserAccountSwitcher(discord.ui.Select):
    def __init__(self, user_accounts, current_player_data):
        current_tag = current_player_data.get("tag", "")
        
        # Create options from user accounts
        options = []
        for account in user_accounts[:25]:  # Discord limit of 25 options
            is_current = account["tag"] == current_tag
            options.append(discord.SelectOption(
                label=f"{account['name']} ({account['tag']})",
                value=account["tag"],
                description="Currently viewing" if is_current else f"Switch to {account['name']}",
                default=is_current
            ))
        
        super().__init__(
            placeholder="Switch account...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.user_accounts = user_accounts
    
    async def callback(self, interaction: discord.Interaction):
        try:
            # Defer the interaction immediately
            await interaction.response.defer()
            
            selected_tag = self.values[0]
            
            # Find the selected account
            selected_account = None
            for account in self.user_accounts:
                if account["tag"] == selected_tag:
                    selected_account = account
                    break
            
            if not selected_account:
                await interaction.followup.send("Account not found.", ephemeral=True)
                return
            
            # Get fresh player data for the selected account
            player_data = await get_coc_player(selected_tag)
            if player_data is None:
                await interaction.followup.send("Failed to fetch player data for selected account.", ephemeral=True)
                return
            
            # Get Discord info for the player tag
            discord_info = await get_discord_info_for_player(selected_tag)
            player_data["discord_info"] = discord_info
            
            # Update the view with new player data
            if self.view.current_view == "Profile Overview":
                new_embed = PlayerEmbeds.player_info(player_data)
            else:
                new_embed = PlayerEmbeds.unit_embed(player_data)
                
            new_view = UserProfileButtonView(player_data, self.user_accounts, self.view.current_view)
            
            await interaction.edit_original_response(embed=new_embed, view=new_view)
        except discord.NotFound:
            # Interaction already handled, ignore
            pass
        except Exception as e:
            print(f"Error in UserAccountSwitcher callback: {e}")

class UserProfileButtonView(discord.ui.View):
    def __init__(self, player_data, user_accounts, current_view="Profile Overview"):
        super().__init__(timeout=None)
        self.player_data = player_data
        self.player_tag = player_data.get("tag", "")
        self.current_view = current_view
        self.user_accounts = user_accounts

        # Add buttons first (row 0)
        self.refresh_btn = discord.ui.Button(
            emoji="🔃",
            style=discord.ButtonStyle.secondary,
            custom_id="refresh_btn_user",
            row=0
        )
        self.refresh_btn.callback = self.refresh_btn_callback
        self.add_item(self.refresh_btn)

        if self.player_tag:
            tag = self.player_tag.replace("#", "")
            url = f"https://link.clashofclans.com/?action=OpenPlayerProfile&tag=%23{tag}"
            self.add_item(discord.ui.Button(
                label="Open In-game",
                url=url,
                style=discord.ButtonStyle.link,
                row=0
            ))

        # Add view selector dropdown (row 1)
        view_selector = ViewSelector(player_data, current_view)
        view_selector.row = 1
        self.add_item(view_selector)
        
        # Add account switcher dropdown (row 2)
        account_switcher = UserAccountSwitcher(user_accounts, player_data)
        account_switcher.row = 2
        self.add_item(account_switcher)

    async def refresh_btn_callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()
            
            # Get fresh player data
            fresh_data = await get_coc_player(self.player_tag)
            if fresh_data is None:
                await interaction.followup.send("❌ Failed to refresh player data.", ephemeral=True)
                return

            # Get Discord info for the refreshed player data
            discord_info = await get_discord_info_for_player(self.player_tag)
            fresh_data["discord_info"] = discord_info

            # Update view with fresh data
            if self.current_view == "Profile Overview":
                embed = PlayerEmbeds.player_info(fresh_data)
            else:
                embed = PlayerEmbeds.unit_embed(fresh_data)

            view = UserProfileButtonView(fresh_data, self.user_accounts, current_view=self.current_view)
            await interaction.edit_original_response(embed=embed, view=view)
        except discord.NotFound:
            pass
        except Exception as e:
            print(f"Error in refresh callback: {e}")
            try:
                await interaction.followup.send("❌ Failed to refresh data.", ephemeral=True)
            except:
                pass



async def get_coc_player(player_tag):
    url = f"https://cocproxy.royaleapi.dev/v1/players/{player_tag.replace('#', '%23')}"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            print(f"get_coc_player failed with status: {resp.status}")
            return None

async def get_discord_info_for_player(player_tag):
    """Get Discord info for a specific player tag"""
    try:
        linked_players_collection = db.linked_players
        cursor = linked_players_collection.find({})
        async for record in cursor:
            verified_tags = [acc.get("tag") for acc in record.get("verified", [])]
            unverified_tags = [acc.get("tag") for acc in record.get("unverified", [])]
            
            if player_tag in verified_tags:
                discord_id = f"<@{record.get('discord_id', 'Not Linked')}>"
                verified_emoji = "<:Verified:1390721846420439051>"
                return f"{discord_id} {verified_emoji}"
            elif player_tag in unverified_tags:
                discord_id = f"<@{record.get('discord_id', 'Not Linked')}>"
                return discord_id
        return "Not Linked"
    except Exception as e:
        print(f"Error querying MongoDB for linked player: {str(e)}")
        return "Not Linked"

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
            user_data = result
            accounts = []
            for account in user_data.get("verified", []) + user_data.get("unverified", []):
                accounts.append({
                    "name": account.get("name", account.get("tag", "Unknown")), 
                    "tag": account.get("tag", "")
                })
            return accounts
        return []
    except Exception as e:
        print(f"MongoDB get_linked_players error: {e}")
        return []

def setup(bot):
    async def player_tag_autocomplete(interaction: discord.Interaction, current: str):
        accounts = await get_linked_players(str(interaction.user.id))
        return [
            discord.app_commands.Choice(
                name=f"{acc['name']} ({acc['tag']})",
                value=acc['tag']
            )
            for acc in accounts
            if current.lower() in acc['tag'].lower() or current.lower() in acc['name'].lower()
        ][:25]

    @bot.tree.command(name="player", description="Get player information")
    @discord.app_commands.describe(
        tag="Player tag (e.g. #2Q82LRL)", 
        user="Select a Discord user to view their linked accounts"
    )
    @discord.app_commands.autocomplete(tag=player_tag_autocomplete)
    async def player_command(interaction: discord.Interaction, tag: str = None, user: discord.User = None):
        await interaction.response.defer()
        
        # Validate input - must provide either tag or user
        if not tag and not user:
            await interaction.followup.send("Please provide either a player tag or select a Discord user.", ephemeral=True)
            return
        
        if tag and user:
            await interaction.followup.send("Please provide either a player tag OR a Discord user, not both.", ephemeral=True)
            return
        
        # Handle user selection (show all their linked accounts)
        if user:
            from commands.utils import get_linked_accounts
            user_accounts = await get_linked_accounts(user.id)
            
            if not user_accounts:
                await interaction.followup.send(f"{user.mention} has no linked accounts.", ephemeral=True)
                return
            
            if len(user_accounts) == 1:
                # Single account - show directly
                account = user_accounts[0]
                player_data = await get_coc_player(account["tag"])
                if not player_data:
                    await interaction.followup.send(f"Failed to fetch data for {account['name']} ({account['tag']}).", ephemeral=True)
                    return
                
                # Get Discord info for the player
                discord_info = await get_discord_info_for_player(account["tag"])
                player_data["discord_info"] = discord_info
                
                view = ProfileButtonView(player_data, current_view="Profile Overview")
                embed = PlayerEmbeds.player_info(player_data)
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            else:
                # Multiple accounts - show with account switcher
                primary_account = user_accounts[0]
                player_data = await get_coc_player(primary_account["tag"])
                if not player_data:
                    await interaction.followup.send(f"Failed to fetch data for {primary_account['name']} ({primary_account['tag']}).", ephemeral=True)
                    return
                
                # Get Discord info for the player
                discord_info = await get_discord_info_for_player(primary_account["tag"])
                player_data["discord_info"] = discord_info
                
                view = UserProfileButtonView(player_data, user_accounts, current_view="Profile Overview")
                embed = PlayerEmbeds.player_info(player_data)
                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        
        # Handle tag selection (original functionality)
        else:
            player_data = await get_coc_player(tag)
            if not player_data:
                await interaction.followup.send("No account found for the provided tag.", ephemeral=True)
                return

            # Check for name changes and update database if needed
            player_tag = player_data.get("tag", "")
            player_name = player_data.get("name", "")
            if player_tag and player_name:
                await update_player_name_if_changed(player_tag, player_name)

            # Get Discord info for the player
            discord_info = await get_discord_info_for_player(player_tag)
            player_data["discord_info"] = discord_info

            view = ProfileButtonView(player_data, current_view="Profile Overview")
            embed = PlayerEmbeds.player_info(player_data)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)