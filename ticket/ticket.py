import disnake
from disnake import app_commands
from .utils import get_guild_data, save_guild_data, get_staff_role, get_category_id, get_welcome_embed_data, get_panel_embed_data, get_button_data, show_profile, parse_discohook_link, get_panel_names

class TicketPanelView(disnake.ui.View):
    def __init__(self, button_label="🎟️ Create Ticket", button_color=disnake.ButtonStyle.primary, panel_name=None):
        super().__init__(timeout=None)
        self.panel_name = panel_name
        self.add_item(TicketButton(button_label, button_color, panel_name))

class TicketButton(disnake.ui.Button):
    def __init__(self, label, style, panel_name):
        super().__init__(label=label, style=style, custom_id=f"apply_now_{panel_name}")
        self.panel_name = panel_name

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

        staff_role = await get_staff_role(interaction.guild, self.panel_name)
        staff_role_id = staff_role.id if staff_role else None
        await interaction.response.send_modal(TagModal(staff_role_id, normalized_username, self.panel_name))

class TagModal(disnake.ui.Modal):
    tag = disnake.ui.TextInput(
        label="Player Tag",
        placeholder="e.g. #2Q82LRL",
        required=True,
        min_length=5,
        max_length=15,
        custom_id="player_tag"
    )

    def __init__(self, staff_role_id, username, panel_name):
        super().__init__(title="Enter In-game Tag")
        self.staff_role_id = staff_role_id
        self.username = username
        self.panel_name = panel_name

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

        staff_role = await get_staff_role(guild, self.panel_name)
        if not staff_role:
            await interaction.followup.send("Staff role is not set up correctly for this server. Please run the /clan-apply-config command.", ephemeral=True)
            return

        if found_channel:
            embed = disnake.Embed(
                description=f"You already have a ticket: {found_channel.mention}",
                color=disnake.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        category_id = await get_category_id(guild, self.panel_name)
        category = guild.get_channel(category_id) if category_id else None

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

        welcome_embed_data = await get_welcome_embed_data(guild.id, self.panel_name)
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
            await interaction.response.send_message("Staff role is not set up. Please run the /clan-apply-config command.", ephemeral=True)
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
    def __init__(self, guild_id=None, panel_name=None):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.panel_name = panel_name

    @disnake.ui.button(label="Confirm Delete", style=disnake.ButtonStyle.danger)
    async def confirm(self, interaction: disnake.ApplicationCommandInteraction, button: disnake.ui.Button):
        await interaction.channel.delete()

def setup(bot):
    async def panel_autocomplete(interaction: disnake.ApplicationCommandInteraction, current: str) -> list[disnake.OptionChoice]:
        panel_names = await get_panel_names(interaction.guild.id)
        return [
            disnake.OptionChoice(name=name, value=name)
            for name in panel_names
            if current.lower() in name.lower()
        ][:25]  # Discord limits autocomplete to 25 choices

    @bot.slash_command(
        name="ticket-panel",
        description="Create, update, or delete a ticket panel configuration"
    )
    async def ticket_panel_command(
        interaction: disnake.ApplicationCommandInteraction,
        name: str,
        delete: bool = False,
        panel_embed: str = None,
        welcome_embed: str = None,
        button_label: str = None,
        button_color: str = None
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Handle delete action
        if delete:
            panel_data = await get_guild_data(interaction.guild.id, name)
            if not panel_data:
                await interaction.followup.send(f"❌ No panel configuration found for '{name}'!", ephemeral=True)
                return
            
            # Delete the panel
            from .utils import delete_guild_data
            await delete_guild_data(interaction.guild.id, name)
            await interaction.followup.send(f"✅ Panel '{name}' has been deleted successfully!", ephemeral=True)
            return

        # Validate required fields for create/update
        if not panel_embed:
            await interaction.followup.send("❌ Panel embed is required when creating or updating a panel!", ephemeral=True)
            return

        # Check panel limit (max 3 panels per server)
        existing_panels = await get_panel_names(interaction.guild.id)
        panel_exists = name in existing_panels
        if not panel_exists and len(existing_panels) >= 3:
            await interaction.followup.send(
                "❌ Maximum of 3 panels allowed per server!\n"
                f"Current panels: {', '.join(existing_panels)}\n"
                "Please delete an existing panel first or use an existing panel name to update it.",
                ephemeral=True
            )
            return

        # Validate panel embed link
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

        # Save panel configuration (overwrites if exists)
        await save_guild_data(
            interaction.guild.id,
            name,
            panel_embed_data=panel_embed_data,
            welcome_embed_data=welcome_embed_data,
            button_label=button_label or "🎟️ Create Ticket",
            button_color=button_color or "primary"
        )

        action = "updated" if panel_exists else "created"
        await interaction.followup.send(
            f"✅ Panel '{name}' configuration has been {action} successfully!\n"
            f"**Panel Embed:** ✅ Set\n"
            f"**Welcome Embed:** {'✅ Set' if welcome_embed_data else '❌ Default'}\n"
            f"**Button Label:** {button_label or '🎟️ Create Ticket'}\n"
            f"**Button Color:** {button_color.title() if button_color else 'Blue'}\n\n"
            f"Use `/ticket-post` to send the panel to a channel.",
            ephemeral=True
        )

    @bot.slash_command(
        name="ticket-post",
        description="Send a ticket panel to a channel"
    )
    async def ticket_post_command(
        interaction: disnake.ApplicationCommandInteraction,
        name: str,
        channel: disnake.TextChannel = None
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Check if panel exists
        panel_data = await get_guild_data(interaction.guild.id, name)
        if not panel_data:
            await interaction.followup.send(f"❌ No panel configuration found for '{name}'!", ephemeral=True)
            return

        # Check if staff role is set
        staff_role = await get_staff_role(interaction.guild, name)
        if not staff_role:
            await interaction.followup.send(
                "❌ Staff roles missing. Use `/ticket-settings` to set a staff role.",
                ephemeral=True
            )
            return

        # Get panel embed data
        panel_embed_data = await get_panel_embed_data(interaction.guild.id, name)
        if not panel_embed_data:
            await interaction.followup.send("❌ Failed to retrieve panel embed data.", ephemeral=True)
            return

        # Get button data
        button_label, button_color = await get_button_data(interaction.guild.id, name)
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
                view=TicketPanelView(button_label, button_style, name)
            )
        else:
            await target_channel.send(
                content=panel_content or "Ticket Panel",
                view=TicketPanelView(button_label, button_style, name)
            )

        await interaction.followup.send(
            f"✅ Panel '{name}' sent successfully to {target_channel.mention}!\n"
            f"**Button:** {button_label}\n"
            f"**Color:** {button_color.title() if button_color else 'Blue'}",
            ephemeral=True
        )



    @bot.slash_command(
        name="ticket-settings",
        description="Configure staff role and category for ticket panels"
    )
    async def ticket_settings_command(
        interaction: disnake.ApplicationCommandInteraction,
        name: str,
        staff_role: disnake.Role = None,
        category: disnake.CategoryChannel = None
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # Check if any changes were provided
        if not staff_role and not category:
            await interaction.followup.send(
                "❌ No changes provided! Please specify at least one option (staff role or category) to update.",
                ephemeral=True
            )
            return

        # Get existing panel data (if any)
        existing_data = await get_guild_data(interaction.guild.id, name)

        # If no existing data, create a new entry with the provided name, staff role, and category
        if not existing_data:
            await save_guild_data(
                interaction.guild.id,
                name,
                staff_role_id=staff_role.id if staff_role else None,
                category_id=category.id if category else None
            )
            updates = []
            if staff_role:
                updates.append(f"**Staff Role:** {staff_role.mention}")
            if category:
                updates.append(f"**Category:** {category.mention}")
            await interaction.followup.send(
                f"✅ Configuration for panel '{name}' created successfully!\n" + "\n".join(updates) +
                f"\n\nUse `/ticket-panel` to set up the panel embed and other settings.",
                ephemeral=True
            )
            return

        # Update existing configuration, preserving other fields
        new_staff_role_id = staff_role.id if staff_role else existing_data.get("staff_role_id")
        new_category_id = category.id if category else existing_data.get("category_id")

        await save_guild_data(
            interaction.guild.id,
            name,
            new_staff_role_id,
            new_category_id,
            existing_data.get("panel_embed_data"),
            existing_data.get("welcome_embed_data"),
            existing_data.get("button_label"),
            existing_data.get("button_color")
        )

        # Build response showing what was updated
        updates = []
        if staff_role:
            updates.append(f"**Staff Role:** {staff_role.mention}")
        if category:
            updates.append(f"**Category:** {category.mention}")

        await interaction.followup.send(
            f"✅ Configuration for panel '{name}' updated successfully!\n" + "\n".join(updates),
            ephemeral=True
        )