import disnake
from .utils import (
    load_config, get_staff_role, get_category_id, get_welcome_embed_data, 
    get_panel_embed_data, get_button_data, create_embed_from_data, 
    get_button_style, show_profile
)

class TicketPanelView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        config = load_config()
        if config:
            button_label = config.get("button_label", "🎟️ Create Ticket")
            button_color = config.get("button_color", "primary")
            button_style = get_button_style(button_color)
            self.add_item(TicketButton(button_label, button_style))

class TicketButton(disnake.ui.Button):
    def __init__(self, label, style):
        super().__init__(label=label, style=style, custom_id="create_ticket_button")

    async def callback(self, interaction: disnake.ApplicationCommandInteraction):
        # Check if user already has a ticket
        normalized_username = interaction.user.name.lower().replace('.', '')
        channel_name = f"ticket-{normalized_username}"
        found_channel = None
        
        for channel in interaction.guild.text_channels:
            if channel.name == channel_name:
                found_channel = channel
                break
                
        if found_channel:
            embed = disnake.Embed(
                description=f"You already have an active ticket: {found_channel.mention}",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get staff role
        staff_role = await get_staff_role(interaction.guild)
        staff_role_id = staff_role.id if staff_role else None
        
        await interaction.response.send_modal(TagModal(staff_role_id, normalized_username))

class TagModal(disnake.ui.Modal):
    tag = disnake.ui.TextInput(
        label="Player Tag",
        placeholder="e.g. #2Q82LRL",
        required=True,
        min_length=5,
        max_length=15,
        custom_id="player_tag"
    )

    def __init__(self, staff_role_id, username):
        super().__init__(title="Enter In-game Tag")
        self.staff_role_id = staff_role_id
        self.username = username

    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer(ephemeral=True)
        
        player_tag = self.tag.value
        if not player_tag.startswith('#'):
            player_tag = '#' + player_tag

        # Get category for tickets
        category_id = await get_category_id()
        category = None
        if category_id:
            try:
                category = interaction.guild.get_channel(int(category_id))
            except (ValueError, TypeError):
                pass

        # Create ticket channel
        overwrites = {
            interaction.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            interaction.user: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        
        if self.staff_role_id:
            staff_role = interaction.guild.get_role(self.staff_role_id)
            if staff_role:
                overwrites[staff_role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

        try:
            channel = await interaction.guild.create_text_channel(
                name=f"ticket-{self.username}",
                category=category,
                overwrites=overwrites,
                topic=f"Support ticket for {interaction.user.display_name} ({player_tag})"
            )
        except Exception as e:
            error_embed = disnake.Embed(
                title="❌ Error",
                description=f"Failed to create ticket channel: {str(e)}",
                color=disnake.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
            return

        # Send welcome message
        welcome_embed_data = await get_welcome_embed_data()
        if welcome_embed_data:
            welcome_embed = create_embed_from_data(welcome_embed_data, user=interaction.user.mention)
        else:
            # Default welcome embed
            welcome_embed = disnake.Embed(
                title="🎫 Ticket Created",
                description=f"Welcome {interaction.user.mention}! Please provide details about your issue.",
                color=disnake.Color.green()
            )

        # Create ticket actions view with player data
        ticket_view = TicketActionsView(self.username, self.staff_role_id, player_data) if player_data else TicketControlsView()
        
        # Tag staff if available
        mention_text = ""
        if self.staff_role_id:
            staff_role = interaction.guild.get_role(self.staff_role_id)
            if staff_role:
                mention_text = f"{staff_role.mention} "

        await channel.send(
            content=f"{mention_text}New ticket created by {interaction.user.mention}",
            embed=welcome_embed,
            view=ticket_view
        )

        # Get player data for the ticket
        from .utils import get_coc_player
        player_data = await get_coc_player(player_tag)
        if not player_data:
            # Send error if player not found
            error_embed = disnake.Embed(
                title="⚠️ Player Not Found",
                description=f"Could not find player with tag {player_tag}. Please verify the tag is correct.",
                color=disnake.Color.orange()
            )
            await channel.send(embed=error_embed)

        # Confirm ticket creation
        success_embed = disnake.Embed(
            title="✅ Ticket Created",
            description=f"Your ticket has been created: {channel.mention}",
            color=disnake.Color.green()
        )
        await interaction.followup.send(embed=success_embed, ephemeral=True)

class TicketActionsView(disnake.ui.View):
    def __init__(self, username, staff_role_id, player_data):
        super().__init__(timeout=None)
        self.username = username
        self.staff_role_id = staff_role_id
        self.player_data = player_data

    @disnake.ui.button(label="Player Account", style=disnake.ButtonStyle.primary, custom_id="profile_button")
    async def profile(self, interaction: disnake.ApplicationCommandInteraction, button: disnake.ui.Button):
        if interaction.user.name.lower() != self.username:
            await interaction.response.send_message("Only the ticket creator can view the profile.", ephemeral=True)
            return
        from .utils import show_profile
        await show_profile(interaction, self.player_data)

    @disnake.ui.button(label="🔒 Close Ticket", style=disnake.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, button: disnake.ui.Button, interaction: disnake.ApplicationCommandInteraction):
        # Check if user has permission to close ticket
        config = load_config()
        if config and config.get("staff_role_id"):
            staff_role = interaction.guild.get_role(int(config["staff_role_id"]))
            if staff_role not in interaction.user.roles and interaction.channel.permissions_for(interaction.user).manage_channels == False:
                await interaction.response.send_message("❌ You don't have permission to close this ticket.", ephemeral=True)
                return

        await interaction.response.send_modal(CloseTicketModal())

class TicketControlsView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="🔒 Close Ticket", style=disnake.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, button: disnake.ui.Button, interaction: disnake.ApplicationCommandInteraction):
        # Check if user has permission to close ticket
        config = load_config()
        if config and config.get("staff_role_id"):
            staff_role = interaction.guild.get_role(int(config["staff_role_id"]))
            if staff_role not in interaction.user.roles and interaction.channel.permissions_for(interaction.user).manage_channels == False:
                await interaction.response.send_message("❌ You don't have permission to close this ticket.", ephemeral=True)
                return

        await interaction.response.send_modal(CloseTicketModal())

class CloseTicketModal(disnake.ui.Modal):
    reason = disnake.ui.TextInput(
        label="Reason for closing (optional)",
        placeholder="Resolved, duplicate, etc.",
        required=False,
        max_length=200,
        style=disnake.TextInputStyle.paragraph
    )

    def __init__(self):
        super().__init__(title="Close Ticket")

    async def callback(self, interaction: disnake.ModalInteraction):
        await interaction.response.defer()
        
        reason = self.reason.value or "No reason provided"
        
        # Create close confirmation embed
        close_embed = disnake.Embed(
            title="🔒 Ticket Closed",
            description=f"This ticket was closed by {interaction.user.mention}\n**Reason:** {reason}",
            color=disnake.Color.red(),
            timestamp=interaction.created_at
        )
        
        await interaction.followup.send(embed=close_embed)
        
        # Delete channel after 5 seconds
        await interaction.channel.edit(name=f"closed-{interaction.channel.name}")
        import asyncio
        await asyncio.sleep(5)
        await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")

def setup(bot):
    """Setup function for the ticket system"""
    # Add persistent views
    bot.add_view(TicketPanelView())
    bot.add_view(TicketControlsView())
    # Note: TicketActionsView is created dynamically with player data
    
    print("Ticket system loaded successfully!")
