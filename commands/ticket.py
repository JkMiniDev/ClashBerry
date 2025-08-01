import discord
from commands.utils import get_config, get_staff_role, get_category_id, get_welcome_embed_data, get_panel_embed_data, get_button_data, show_profile, get_linked_accounts

class TicketPanelView(discord.ui.View):
    def __init__(self, button_label="🎟️ Create Ticket", button_color=discord.ButtonStyle.primary):
        super().__init__(timeout=None)
        self.add_item(TicketButton(button_label, button_color))

class TicketButton(discord.ui.Button):
    def __init__(self, label, style):
        super().__init__(label=label, style=style, custom_id="create_ticket")

    async def callback(self, interaction: discord.Interaction):
        try:
            # Check if interaction is already handled
            if interaction.response.is_done():
                return
            
            # Defer immediately to prevent timeout
            await interaction.response.defer(ephemeral=True)
            
            config = get_config()
            
            # Check if this is the configured server
            if str(interaction.guild.id) != config.get("server_id"):
                await interaction.followup.send("This ticket system is not configured for this server.", ephemeral=True)
                return
                
            normalized_username = interaction.user.name.lower().replace('.', '')
            channel_name = f"ticket-{normalized_username}"
            found_channel = None
            for channel in interaction.guild.text_channels:
                if channel.name == channel_name:
                    found_channel = channel
                    break
            if found_channel:
                embed = discord.Embed(
                    description=f"You have already opened a ticket: {found_channel.mention}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Check for linked accounts first
            linked_accounts = await get_linked_accounts(interaction.user.id)
            
            if linked_accounts and len(linked_accounts) > 1:
                # Fetch town hall data for all accounts
                account_th_data = {}
                for account in linked_accounts:
                    try:
                        from commands.utils import get_coc_player
                        player_data_temp = await get_coc_player(account["tag"])
                        if player_data_temp:
                            account_th_data[account["tag"]] = player_data_temp.get('townHallLevel', 1)
                    except:
                        account_th_data[account["tag"]] = 1  # Default to TH1
                
                # Show account selection if multiple accounts
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="Select Accounts",
                        description="You have multiple linked accounts. Please select which accounts you want to use for this ticket (you can select multiple):",
                        color=discord.Color.blue()
                    ),
                    view=AccountSelectionView(linked_accounts, normalized_username, account_th_data),
                    ephemeral=True
                )
            elif linked_accounts and len(linked_accounts) == 1:
                # Auto-use single linked account
                account = linked_accounts[0]
                staff_role = get_staff_role(interaction.guild)
                await self.create_ticket_with_account(interaction, account["tag"], account["name"], normalized_username, staff_role, linked_accounts, None)
            else:
                # No linked accounts, show manual tag entry
                staff_role = get_staff_role(interaction.guild)
                staff_role_id = staff_role.id if staff_role else None
                # Can't use followup for modals, need to use response
                # But interaction was already deferred, so this will fail
                # Need a different approach - send a message with instructions
                embed = discord.Embed(
                    title="Manual Tag Entry",
                    description="You don't have any linked accounts. Please use the linkaccount command first to link your accounts, then try creating a ticket again.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
        
        except discord.NotFound:
            # Interaction already handled or expired, ignore
            print(f"Interaction already handled for user {interaction.user.id}")
            pass
        except Exception as e:
            print(f"Error in ticket button callback: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message("❌ An error occurred. Please try again.", ephemeral=True)
                else:
                    await interaction.followup.send("❌ An error occurred. Please try again.", ephemeral=True)
            except:
                pass
    
    async def create_ticket_with_account(self, interaction, player_tag, player_name, normalized_username, staff_role, all_linked_accounts, account_th_data=None):
        """Create ticket with selected account"""
        from commands.utils import get_coc_player
        
        # Get fresh player data
        player_data = await get_coc_player(player_tag)
        if player_data is None:
            if interaction.response.is_done():
                await interaction.followup.send("😓 Failed to fetch player data.", ephemeral=True)
            else:
                await interaction.response.send_message("😓 Failed to fetch player data.", ephemeral=True)
            return

        guild = interaction.guild
        user = interaction.user
        channel_name = f"ticket-{normalized_username}"
        
        # Check for existing ticket
        found_channel = None
        for channel in guild.text_channels:
            if channel.name == channel_name:
                found_channel = channel
                break

        if found_channel:
            embed = discord.Embed(
                description=f"You already have a ticket: {found_channel.mention}",
                color=discord.Color.red()
            )
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not staff_role:
            if interaction.response.is_done():
                await interaction.followup.send("Staff role is not configured properly.", ephemeral=True)
            else:
                await interaction.response.send_message("Staff role is not configured properly.", ephemeral=True)
            return

        category_id = get_category_id()
        category = guild.get_channel(category_id) if category_id else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }

        # Defer the response if not already done
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason="Clan application ticket"
        )

        welcome_embed_data = get_welcome_embed_data()
        if welcome_embed_data:
            welcome_embed = discord.Embed.from_dict(welcome_embed_data)
        else:
            welcome_embed = discord.Embed(
                title="Clan Application",
                description=(
                    f"Welcome to the clan application.\n\n"
                    f"**Current Account:** {player_data.get('name', 'Unknown')} ({player_data.get('tag', 'Unknown')})\n\n"
                    f"Your ticket will be handled shortly."
                ),
                color=discord.Color.green()
            )

        staff_mention = staff_role.mention if staff_role else "@Staff"

        # Use MultiAccountTicketActionsView if multiple accounts, otherwise regular view
        if len(all_linked_accounts) > 1:
            actions_view = MultiAccountTicketActionsView(user.name.lower(), staff_role.id if staff_role else None, player_data, all_linked_accounts, account_th_data)
        else:
            actions_view = TicketActionsView(user.name.lower(), staff_role.id if staff_role else None, player_data)
        
        ticket_message = await ticket_channel.send(
            content=f"{user.mention} {staff_mention}",
            embed=welcome_embed,
            view=actions_view
        )
        await ticket_message.pin()

        confirm_embed = discord.Embed(
            title="✅ Ticket Created",
            description=f"Your ticket has been created: {ticket_channel.mention}",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

class TagModal(discord.ui.Modal, title="Enter In-game Tag"):
    tag = discord.ui.TextInput(
        label="Player Tag",
        placeholder="e.g. #2Q82LRL",
        required=True,
        min_length=5,
        max_length=15
    )

    def __init__(self, staff_role_id, username):
        super().__init__()
        self.staff_role_id = staff_role_id
        self.username = username

    async def on_submit(self, interaction: discord.Interaction):
        from commands.utils import get_coc_player
        player_tag = self.tag.value.replace(" ", "").upper().replace("O", "0")
        if not player_tag.startswith("#"):
            player_tag = "#" + player_tag

        await interaction.response.defer(ephemeral=True, thinking=True)
        player_data = await get_coc_player(player_tag)
        if player_data is None:
            await interaction.followup.send("😓 Invalid player tag.", ephemeral=True)
            return

        guild = interaction.guild
        user = interaction.user
        channel_name = f"ticket-{user.name.lower()}"
        found_channel = None
        for channel in guild.text_channels:
            if channel.name == channel_name:
                found_channel = channel
                break

        staff_role = get_staff_role(guild)
        if not staff_role:
            await interaction.followup.send("Staff role is not configured properly.", ephemeral=True)
            return

        if found_channel:
            embed = discord.Embed(
                description=f"You already have a ticket: {found_channel.mention}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        category_id = get_category_id()
        category = guild.get_channel(category_id) if category_id else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason="Clan application ticket"
        )

        welcome_embed_data = get_welcome_embed_data()
        if welcome_embed_data:
            welcome_embed = discord.Embed.from_dict(welcome_embed_data)
        else:
            welcome_embed = discord.Embed(
                title="Clan Application",
                description=(
                    f"Welcome to the clan application.\n\n"
                    f"Your ticket will be handled shortly."
                ),
                color=discord.Color.green()
            )

        staff_mention = staff_role.mention if staff_role else "@Staff"

        # Check if user has multiple accounts for the dropdown
        all_linked_accounts = await get_linked_accounts(user.id)
        
        # Use MultiAccountTicketActionsView if multiple accounts, otherwise regular view
        if len(all_linked_accounts) > 1:
            actions_view = MultiAccountTicketActionsView(user.name.lower(), staff_role.id if staff_role else None, player_data, all_linked_accounts, account_th_data)
        else:
            actions_view = TicketActionsView(user.name.lower(), staff_role.id if staff_role else None, player_data)

        ticket_message = await ticket_channel.send(
            content=f"{user.mention} {staff_mention}",
            embed=welcome_embed,
            view=actions_view
        )
        await ticket_message.pin()

        confirm_embed = discord.Embed(
            title="✅ Ticket Created",
            description=f"Your ticket has been created: {ticket_channel.mention}",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

class TicketActionsView(discord.ui.View):
    def __init__(self, username, staff_role_id, player_data):
        super().__init__(timeout=None)
        self.username = username
        self.staff_role_id = staff_role_id
        self.player_data = player_data

    @discord.ui.button(label="Player Account", style=discord.ButtonStyle.primary, custom_id="profile_button")
    async def profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_profile(interaction, self.player_data)

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.danger, custom_id="delete_ticket")
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = get_staff_role(interaction.guild)
        if not staff_role:
            await interaction.response.send_message("Staff role is not configured.", ephemeral=True)
            return
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("Please ask staff to delete this ticket.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Delete Confirmation",
            description="Are you sure you want to delete this ticket?",
            color=discord.Color.red()
        )
        await interaction.response.send_message(
            embed=embed,
            view=DeleteConfirmView(),
            ephemeral=True
        )

class DeleteConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

def setup(bot):
    pass  # No commands to register
class AccountSelectionView(discord.ui.View):
    def __init__(self, linked_accounts, normalized_username, account_th_data=None):
        super().__init__(timeout=300)
        self.linked_accounts = linked_accounts
        self.normalized_username = normalized_username
        self.selected_accounts = []
        self.account_th_data = account_th_data or {}
        
        # Add account selection checkboxes (up to 25 accounts)
        for i, account in enumerate(linked_accounts[:25]):
            self.add_item(AccountCheckboxButton(account, i, self.account_th_data.get(account["tag"])))
    
    @discord.ui.button(label="Confirm Selection", style=discord.ButtonStyle.green, row=4)
    async def confirm_selection(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.selected_accounts:
            await interaction.response.send_message("Please select at least one account.", ephemeral=True)
            return
        
        staff_role = get_staff_role(interaction.guild)
        
        # Create ticket with selected accounts (use first account as primary)
        primary_account = self.selected_accounts[0]
        ticket_button = TicketButton("", discord.ButtonStyle.primary)
        
        # Create th_data for selected accounts only
        selected_th_data = {}
        for account in self.selected_accounts:
            if account["tag"] in self.account_th_data:
                selected_th_data[account["tag"]] = self.account_th_data[account["tag"]]
        
        await ticket_button.create_ticket_with_account(
            interaction, 
            primary_account["tag"], 
            primary_account["name"], 
            self.normalized_username, 
            staff_role,
            self.selected_accounts, # Pass only selected accounts to the callback
            selected_th_data
        )

class AccountCheckboxButton(discord.ui.Button):
    def __init__(self, account, index, th_level=None):
        # Get town hall emoji
        from commands.utils import PlayerEmbeds
        th_emoji = PlayerEmbeds.TH_EMOJIS.get(str(th_level)) if th_level else None
        
        super().__init__(
            label=f"{account['name']} ({account['tag']})",
            style=discord.ButtonStyle.secondary,
            emoji=th_emoji,
            row=index // 5  # 5 buttons per row
        )
        self.account = account
        self.is_selected = False
        self.th_level = th_level
    
    async def callback(self, interaction: discord.Interaction):
        self.is_selected = not self.is_selected
        
        if self.is_selected:
            self.style = discord.ButtonStyle.green
            self.label = f"✅ {self.account['name']} ({self.account['tag']})"
            if self.account not in self.view.selected_accounts:
                self.view.selected_accounts.append(self.account)
        else:
            self.style = discord.ButtonStyle.secondary
            self.label = f"{self.account['name']} ({self.account['tag']})"
            if self.account in self.view.selected_accounts:
                self.view.selected_accounts.remove(self.account)
        
        await interaction.response.edit_message(view=self.view)

class AccountSelectionDropdown(discord.ui.Select):
    def __init__(self, linked_accounts, account_th_data=None):
        # Create options from linked accounts
        options = []
        for i, account in enumerate(linked_accounts[:25]):  # Discord limit of 25 options
            # Get town hall emoji for this account
            from commands.utils import PlayerEmbeds
            th_level = account_th_data.get(account["tag"]) if account_th_data else None
            th_emoji = PlayerEmbeds.TH_EMOJIS.get(str(th_level)) if th_level else None
            
            options.append(discord.SelectOption(
                label=f"{account['name']} ({account['tag']})",
                value=str(i),
                emoji=th_emoji
            ))
        
        super().__init__(
            placeholder="Choose an account...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.linked_accounts = linked_accounts
    
    async def callback(self, interaction: discord.Interaction):
        selected_index = int(self.values[0])
        selected_account = self.linked_accounts[selected_index]
        
        # Update parent view's selected accounts
        self.view.selected_accounts = [selected_account]
        
        await interaction.response.send_message(
            f"Selected: **{selected_account['name']} ({selected_account['tag']})**",
            ephemeral=True
        )

class MultiAccountTicketActionsView(discord.ui.View):
    def __init__(self, username, staff_role_id, current_player_data, all_linked_accounts, account_th_data=None):
        super().__init__(timeout=None)
        self.username = username
        self.staff_role_id = staff_role_id
        self.current_player_data = current_player_data
        self.all_linked_accounts = all_linked_accounts
        self.account_th_data = account_th_data or {}
    
    @discord.ui.button(label="Player Account", style=discord.ButtonStyle.primary, custom_id="profile_button", row=1)
    async def profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_profile(interaction, self.current_player_data, self.all_linked_accounts, self.account_th_data)

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.danger, custom_id="delete_ticket", row=1)
    async def delete_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = get_staff_role(interaction.guild)
        if not staff_role:
            await interaction.response.send_message("Staff role is not configured.", ephemeral=True)
            return
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("Please ask staff to delete this ticket.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Delete Confirmation",
            description="Are you sure you want to delete this ticket?",
            color=discord.Color.red()
        )
        await interaction.response.send_message(
            embed=embed,
            view=DeleteConfirmView(),
            ephemeral=True
        )

class AccountSwitcherDropdown(discord.ui.Select):
    def __init__(self, all_linked_accounts, current_player_data):
        current_tag = current_player_data.get("tag", "")
        
        # Create options from linked accounts
        options = []
        for account in all_linked_accounts[:25]:  # Discord limit of 25 options
            is_current = account["tag"] == current_tag
            options.append(discord.SelectOption(
                label=f"{account['name']} ({account['tag']})",
                value=account["tag"],
                description="Currently selected" if is_current else f"Switch to {account['name']}",
                default=is_current
            ))
        
        super().__init__(
            placeholder="Switch account...",
            min_values=1,
            max_values=1,
            options=options,
            row=0
        )
        self.all_linked_accounts = all_linked_accounts
    
    async def callback(self, interaction: discord.Interaction):
        selected_tag = self.values[0]
        
        # Find the selected account
        selected_account = None
        for account in self.all_linked_accounts:
            if account["tag"] == selected_tag:
                selected_account = account
                break
        
        if not selected_account:
            await interaction.response.send_message("Account not found.", ephemeral=True)
            return
        
        # Get fresh player data for the selected account
        from .utils import get_coc_player
        player_data = await get_coc_player(selected_tag)
        if player_data is None:
            await interaction.response.send_message("Failed to fetch player data for selected account.", ephemeral=True)
            return
        
        # Update the view with new player data
        new_view = MultiAccountTicketActionsView(
            self.view.username, 
            self.view.staff_role_id, 
            player_data, 
            self.all_linked_accounts,
            getattr(self.view, 'account_th_data', {})
        )
        
        # Update the welcome embed
        welcome_embed_data = get_welcome_embed_data()
        if welcome_embed_data:
            welcome_embed = discord.Embed.from_dict(welcome_embed_data)
        else:
            welcome_embed = discord.Embed(
                title="Clan Application",
                description=(
                    f"Welcome to the clan application.\n\n"
                    f"**Current Account:** {player_data.get('name', 'Unknown')} ({player_data.get('tag', 'Unknown')})\n\n"
                    f"Your ticket will be handled shortly."
                ),
                color=discord.Color.green()
            )
        
        await interaction.response.edit_message(embed=welcome_embed, view=new_view)
