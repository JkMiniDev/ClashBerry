import discord
from .utils import get_config, get_staff_role, get_category_id, get_welcome_embed_data, get_panel_embed_data, get_button_data, show_profile

class TicketPanelView(discord.ui.View):
    def __init__(self, button_label="🎟️ Create Ticket", button_color=discord.ButtonStyle.primary):
        super().__init__(timeout=None)
        self.add_item(TicketButton(button_label, button_color))

class TicketButton(discord.ui.Button):
    def __init__(self, label, style):
        super().__init__(label=label, style=style, custom_id="create_ticket")

    async def callback(self, interaction: discord.Interaction):
        config = get_config()
        
        # Check if this is the configured server
        if str(interaction.guild.id) != config.get("server_id"):
            await interaction.response.send_message("This ticket system is not configured for this server.", ephemeral=True)
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
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        staff_role = get_staff_role(interaction.guild)
        staff_role_id = staff_role.id if staff_role else None
        await interaction.response.send_modal(TagModal(staff_role_id, normalized_username))

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
        from .utils import get_coc_player
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

        ticket_message = await ticket_channel.send(
            content=f"{user.mention} {staff_mention}",
            embed=welcome_embed,
            view=TicketActionsView(user.name.lower(), staff_role.id if staff_role else None, player_data)
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