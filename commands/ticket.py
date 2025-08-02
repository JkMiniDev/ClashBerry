import discord
from commands.utils import get_config, get_staff_role, get_category_id, get_welcome_embed_data, get_panel_embed_data, get_button_data, get_linked_accounts, show_profile, PlayerEmbeds

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
                        title="🔐 Select Account(s)",
                        description="**Select at least 1**\n\nChoose which accounts you want to use for this ticket.",
                        color=0x5865F2  # Discord blurple color
                    ),
                    view=AccountDropdownView(linked_accounts, normalized_username, account_th_data),
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

async def send_panel_to_channel(bot, message, target_channel=None):
    """Send ticket panel to specified channel or current channel (Admin only)"""
    # Check if user has admin permissions
    if not message.author.guild_permissions.administrator:
        # Silently ignore - no response
        return
    
    # Use specified channel or current channel
    target_channel = target_channel or message.channel
    
    # Check if bot has permissions in target channel
    bot_permissions = target_channel.permissions_for(message.guild.me)
    if not (bot_permissions.send_messages and bot_permissions.embed_links):
        await message.channel.send(
            "❌ I don't have permission to send messages or embeds in that channel."
        )
        return
    
    try:
        # Get panel configuration
        from commands.utils import get_panel_embed_data, get_button_data
        
        embed_data = get_panel_embed_data()
        button_data = get_button_data()
        
        # Create embed
        embed = discord.Embed(
            title=embed_data.get("title", "🎫 Ticket System"),
            description=embed_data.get("description", "Click the button below to create a new ticket."),
            color=embed_data.get("color", 5763719)
        )
        
        # Add thumbnail if configured
        thumbnail_url = embed_data.get("thumbnail", {}).get("url")
        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)
        
        # Add footer if configured
        footer_data = embed_data.get("footer", {})
        footer_text = footer_data.get("text")
        footer_icon = footer_data.get("icon_url")
        if footer_text:
            embed.set_footer(text=footer_text, icon_url=footer_icon)
        
        # Create view with ticket button
        button_label = button_data.get("label", "🎟️ Create Ticket")
        button_style_str = button_data.get("color", "primary")
        
        # Convert string to ButtonStyle
        button_style = discord.ButtonStyle.primary
        if button_style_str == "secondary":
            button_style = discord.ButtonStyle.secondary
        elif button_style_str == "success":
            button_style = discord.ButtonStyle.success
        elif button_style_str == "danger":
            button_style = discord.ButtonStyle.danger
        
        view = TicketPanelView(button_label, button_style)
        
        # Send panel to target channel
        panel_message = await target_channel.send(embed=embed, view=view)
        
        # Send confirmation to user
        if target_channel == message.channel:
            await message.channel.send("✅ Ticket panel sent to this channel!")
        else:
            await message.channel.send(f"✅ Ticket panel sent to {target_channel.mention}!")
            
    except Exception as e:
        await message.channel.send(f"❌ Failed to send ticket panel: {str(e)}")

def setup(bot):
    pass  # No commands to register
class AccountDropdownView(discord.ui.View):
    def __init__(self, linked_accounts, normalized_username, account_th_data=None):
        super().__init__(timeout=300)
        self.linked_accounts = linked_accounts
        self.normalized_username = normalized_username
        self.selected_accounts = []
        self.account_th_data = account_th_data or {}
        
        # Add the multi-select dropdown
        self.add_item(AccountMultiSelect(linked_accounts, account_th_data))
    
    async def update_embed(self, interaction):
        """Update the embed with current selection"""
        embed = discord.Embed(
            title="🔐 Select Account(s)",
            description="**Select at least 1**\n\nChoose which accounts you want to use for this ticket.",
            color=0x5865F2  # Discord blurple color
        )
        
        if self.selected_accounts:
            selected_text = ""
            for account in self.selected_accounts:
                th_level = self.account_th_data.get(account["tag"], "?")
                th_emoji = PlayerEmbeds.TH_EMOJIS.get(str(th_level), "🏰")
                selected_text += f"{th_emoji} **{account['name']}** `{account['tag']}`\n"
            
            embed.add_field(
                name=f"✅ Selected ({len(self.selected_accounts)})",
                value=selected_text,
                inline=False
            )
            
            # Show confirm button when accounts are selected
            if not any(isinstance(item, ConfirmSelectionButton) for item in self.children):
                self.add_item(ConfirmSelectionButton())
        else:
            # Remove confirm button if no accounts selected
            for item in self.children[:]:
                if isinstance(item, ConfirmSelectionButton):
                    self.remove_item(item)
        
        embed.set_footer(text="💡 Use the dropdown above to select accounts")
        return embed

class AccountMultiSelect(discord.ui.Select):
    def __init__(self, linked_accounts, account_th_data=None):
        # Create options from linked accounts with checkmark styling
        options = []
        for account in linked_accounts[:25]:  # Discord limit of 25 options
            # Get town hall emoji for this account
            th_level = account_th_data.get(account["tag"]) if account_th_data else None
            th_emoji = PlayerEmbeds.TH_EMOJIS.get(str(th_level)) if th_level else "🏰"
            
            # Create option with account info
            option = discord.SelectOption(
                label=f"{account['name']}",
                description=f"Tag: {account['tag']} • TH: {th_level or '?'}",
                value=account["tag"],
                emoji=th_emoji
            )
            options.append(option)
        
        super().__init__(
            placeholder="🔽 Select accounts for this ticket...",
            min_values=0,
            max_values=len(linked_accounts),  # Allow selecting all accounts
            options=options
        )
        self.linked_accounts = {acc["tag"]: acc for acc in linked_accounts}
        self.account_th_data = account_th_data or {}
    
    async def callback(self, interaction: discord.Interaction):
        # Update selected accounts based on dropdown values
        self.view.selected_accounts = []
        for tag in self.values:
            if tag in self.linked_accounts:
                self.view.selected_accounts.append(self.linked_accounts[tag])
        
        # Update placeholder to show selection count
        if self.values:
            self.placeholder = f"✅ {len(self.values)} account(s) selected"
        else:
            self.placeholder = "🔽 Select accounts for this ticket..."
        
        # Update the embed with current selection
        updated_embed = await self.view.update_embed(interaction)
        await interaction.response.edit_message(embed=updated_embed, view=self.view)

class ConfirmSelectionButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="✅ Create Ticket",
            style=discord.ButtonStyle.success,
            emoji="🎫",
            row=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        if not self.view.selected_accounts:
            error_embed = discord.Embed(
                title="❌ No Selection",
                description="Please select at least one account from the dropdown above.",
                color=0xED4245  # Discord red color
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
        
        # Create loading embed
        loading_embed = discord.Embed(
            title="🎫 Creating Ticket...",
            description="Please wait while we set up your ticket with the selected accounts.",
            color=0xFEE75C  # Discord yellow color
        )
        await interaction.response.edit_message(embed=loading_embed, view=None)
        
        staff_role = get_staff_role(interaction.guild)
        
        # Create ticket with selected accounts (use first account as primary)
        primary_account = self.view.selected_accounts[0]
        ticket_button = TicketButton("", discord.ButtonStyle.primary)
        
        # Create th_data for selected accounts only
        selected_th_data = {}
        for account in self.view.selected_accounts:
            if account["tag"] in self.view.account_th_data:
                selected_th_data[account["tag"]] = self.view.account_th_data[account["tag"]]
        
        await ticket_button.create_ticket_with_account(
            interaction, 
            primary_account["tag"], 
            primary_account["name"], 
            self.view.normalized_username, 
            staff_role,
            self.view.selected_accounts,
            selected_th_data
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
