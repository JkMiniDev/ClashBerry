import disnake
from disnake import app_commands
from .utils import get_staff_role, get_category_id, get_welcome_embed_data, get_panel_embed_data, get_button_data, show_profile, parse_discohook_link, save_ticket_settings

class TicketPanelView(disnake.ui.View):
    def __init__(self, button_label="🎟️ Create Ticket", button_color=disnake.ButtonStyle.primary):
        super().__init__(timeout=None)
        self.add_item(TicketButton(button_label, button_color))

class TicketButton(disnake.ui.Button):
    def __init__(self, label, style):
        super().__init__(label=label, style=style, custom_id="apply_now_ticket")
        self.label = label

    async def callback(self, interaction: disnake.ApplicationCommandInteraction):
        normalized_username = interaction.user.name.lower().replace('.', '')
        channel_name = f"ticket-{normalized_username}"
        found_channel = None
        for channel in interaction.guild.text_channels:
            if channel.name == channel_name:
                found_channel = channel
                break
        if found_channel:
            embed = disnake.Embed(
                description=f"You have already opened a ticket: {found_channel.mention}",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

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

    async def on_submit(self, interaction: disnake.ApplicationCommandInteraction):
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

        staff_role = await get_staff_role(guild)
        if not staff_role:
            await interaction.followup.send("Staff role is not set up correctly. Please run the /ticket-settings command.", ephemeral=True)
            return

        if found_channel:
            embed = disnake.Embed(
                description=f"You already have a ticket: {found_channel.mention}",
                color=disnake.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        category_id = await get_category_id()
        category = guild.get_channel(int(category_id)) if category_id else None

        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(view_channel=False),
            user: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: disnake.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason="Clan application ticket"
        )

        welcome_embed_data = await get_welcome_embed_data()
        if welcome_embed_data and welcome_embed_data.get("embeds"):
            welcome_embeds = [disnake.Embed.from_dict(e) for e in welcome_embed_data["embeds"]]
            welcome_content = welcome_embed_data.get("content")
        else:
            welcome_embeds = [disnake.Embed(
                title="Clan Application",
                description=(
                    f"Welcome to the clan application.\n\n"
                    f"Your ticket will be handled shortly."
                ),
                color=disnake.Color.green()
            )]
            welcome_content = None

        staff_mention = staff_role.mention if staff_role else "@Staff"

        ticket_message = await ticket_channel.send(
            content=f"{user.mention} {staff_mention}" + (f"\n{welcome_content}" if welcome_content else ""),
            embeds=welcome_embeds,
            view=TicketActionsView(user.name.lower(), staff_role.id if staff_role else None, player_data)
        )
        await ticket_message.pin()

        confirm_embed = disnake.Embed(
            title="✅ Ticket Created",
            description=f"Your ticket has been created: {ticket_channel.mention}",
            color=disnake.Color.green()
        )
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

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
        await show_profile(interaction, self.player_data)

    @disnake.ui.button(label="Delete Ticket", style=disnake.ButtonStyle.danger, custom_id="delete_ticket")
    async def delete_ticket(self, interaction: disnake.ApplicationCommandInteraction, button: disnake.ui.Button):
        staff_role = await get_staff_role(interaction.guild)
        if not staff_role:
            await interaction.response.send_message("Staff role is not set up. Please run the /ticket-settings command.", ephemeral=True)
            return
        if staff_role not in interaction.user.roles:
            await interaction.response.send_message("Please ask staff to delete this ticket.", ephemeral=True)
            return

        embed = disnake.Embed(
            title="Delete Confirmation",
            description="Are you sure you want to delete this ticket?",
            color=disnake.Color.red()
        )
        await interaction.response.send_message(
            embed=embed,
            view=DeleteConfirmView(),
            ephemeral=True
        )

class DeleteConfirmView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Confirm Delete", style=disnake.ButtonStyle.danger)
    async def confirm(self, interaction: disnake.ApplicationCommandInteraction, button: disnake.ui.Button):
        await interaction.channel.delete()

def setup(bot):
    @bot.slash_command(
        name="ticket-panel",
        description="Configure the ticket panel settings"
    )
    async def ticket_panel_command(
        interaction: disnake.ApplicationCommandInteraction,
        panel_embed: str = None,
        welcome_embed: str = None,
        button_label: str = None,
        button_color: str = None
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Validate panel embed link if provided
        panel_embed_data = None
        if panel_embed:
            panel_embed_data = await parse_discohook_link(panel_embed)
            if not panel_embed_data:
                await interaction.followup.send("❌ Invalid panel embed link. Please provide a valid Discohook link.", ephemeral=True)
                return

        # Validate welcome embed link if provided
        welcome_embed_data = None
        if welcome_embed:
            welcome_embed_data = await parse_discohook_link(welcome_embed)
            if not welcome_embed_data:
                await interaction.followup.send("❌ Invalid welcome embed link. Please provide a valid Discohook link.", ephemeral=True)
                return

        # Save panel configuration
        success = await save_ticket_settings(
            panel_embed_data=panel_embed_data,
            welcome_embed_data=welcome_embed_data,
            button_label=button_label,
            button_color=button_color
        )

        if success:
            await interaction.followup.send(
                f"✅ Ticket panel configuration updated successfully!\n"
                f"**Panel Embed:** {'✅ Set' if panel_embed_data else '❌ Using Default'}\n"
                f"**Welcome Embed:** {'✅ Set' if welcome_embed_data else '❌ Using Default'}\n"
                f"**Button Label:** {button_label or '🎟️ Create Ticket'}\n"
                f"**Button Color:** {button_color.title() if button_color else 'Primary'}\n\n"
                f"Use `/ticket-post` to send the panel to a channel.",
                ephemeral=True
            )
        else:
            await interaction.followup.send("❌ Failed to save configuration.", ephemeral=True)

    @bot.slash_command(
        name="ticket-post",
        description="Send the ticket panel to a channel"
    )
    async def ticket_post_command(
        interaction: disnake.ApplicationCommandInteraction,
        channel: disnake.TextChannel = None
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Check if staff role is set
        staff_role = await get_staff_role(interaction.guild)
        if not staff_role:
            await interaction.followup.send(
                "❌ Staff role not configured. Use `/ticket-settings` to set a staff role.",
                ephemeral=True
            )
            return

        # Get panel embed data
        panel_embed_data = await get_panel_embed_data()
        if not panel_embed_data:
            await interaction.followup.send("❌ Failed to retrieve panel embed data.", ephemeral=True)
            return

        # Get button data
        button_label, button_color = await get_button_data()
        button_style = disnake.ButtonStyle.primary
        if button_color == "success":
            button_style = disnake.ButtonStyle.success
        elif button_color == "danger":
            button_style = disnake.ButtonStyle.danger
        elif button_color == "secondary":
            button_style = disnake.ButtonStyle.secondary

        # Create panel embed
        panel_embeds = [disnake.Embed.from_dict(e) for e in panel_embed_data.get("embeds", [])]
        panel_content = panel_embed_data.get("content")

        # Send panel to channel (default to interaction channel if not specified)
        target_channel = channel or interaction.channel
        if panel_embeds:
            await target_channel.send(
                content=panel_content,
                embeds=panel_embeds,
                view=TicketPanelView(button_label, button_style)
            )
        else:
            await target_channel.send(
                content=panel_content or "Ticket Panel",
                view=TicketPanelView(button_label, button_style)
            )

        await interaction.followup.send(
            f"✅ Ticket panel sent successfully to {target_channel.mention}!\n"
            f"**Button:** {button_label or '🎟️ Create Ticket'}\n"
            f"**Color:** {button_color.title() if button_color else 'Primary'}",
            ephemeral=True
        )

    @bot.slash_command(
        name="ticket-settings",
        description="Configure server ID, ticket channel, staff role and category"
    )
    async def ticket_settings_command(
        interaction: disnake.ApplicationCommandInteraction,
        server_id: str = None,
        ticket_channel: disnake.TextChannel = None,
        staff_role: disnake.Role = None,
        category: disnake.CategoryChannel = None
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Check if any changes were provided
        if not any([server_id, ticket_channel, staff_role, category]):
            await interaction.followup.send(
                "❌ No changes provided! Please specify at least one option to update.",
                ephemeral=True
            )
            return

        # Save settings
        success = await save_ticket_settings(
            server_id=server_id,
            ticket_channel_id=ticket_channel.id if ticket_channel else None,
            staff_role_id=staff_role.id if staff_role else None,
            category_id=category.id if category else None
        )

        if success:
            # Build response showing what was updated
            updates = []
            if server_id:
                updates.append(f"**Server ID:** {server_id}")
            if ticket_channel:
                updates.append(f"**Ticket Channel:** {ticket_channel.mention}")
            if staff_role:
                updates.append(f"**Staff Role:** {staff_role.mention}")
            if category:
                updates.append(f"**Category:** {category.mention}")

            await interaction.followup.send(
                f"✅ Ticket settings updated successfully!\n" + "\n".join(updates),
                ephemeral=True
            )
        else:
            await interaction.followup.send("❌ Failed to save settings.", ephemeral=True)
