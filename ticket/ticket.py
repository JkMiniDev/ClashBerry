import disnake
from disnake import app_commands
from .utils import get_staff_role, get_category_id, get_welcome_embed_data, get_panel_embed_data, get_button_data, show_profile

class TicketPanelView(disnake.ui.View):
    def __init__(self, button_label="🎟️ Create Ticket", button_color=disnake.ButtonStyle.primary):
        super().__init__(timeout=None)
        self.add_item(TicketButton(button_label, button_color))

class TicketButton(disnake.ui.Button):
    def __init__(self, label, style):
        super().__init__(label=label, style=style, custom_id="apply_now_ticket")
        self.label = label

    async def callback(self, interaction: disnake.MessageInteraction):
        # Create safe username for channel name
        safe_username = ''.join(c for c in interaction.user.display_name.lower() if c.isalnum())[:20]
        if not safe_username:
            safe_username = f"user{interaction.user.id}"
        channel_name = f"ticket-{safe_username}"
        
        # Check for existing ticket using disnake.utils.get
        existing_ticket = disnake.utils.get(interaction.guild.text_channels, name=channel_name)
        if existing_ticket:
            embed = disnake.Embed(
                description=f"You already have an open ticket: {existing_ticket.mention}",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Get staff role
        staff_role = await get_staff_role(interaction.guild)
        if not staff_role:
            embed = disnake.Embed(
                title="❌ Configuration Error",
                description="Staff role is not configured. Please contact an administrator.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Send the modal
        await interaction.response.send_modal(TagModal(staff_role.id, safe_username))

class TagModal(disnake.ui.Modal):
    def __init__(self, staff_role_id, username):
        self.staff_role_id = staff_role_id
        self.username = username
        
        self.tag = disnake.ui.TextInput(
            label="Player Tag",
            placeholder="e.g. #2Q82LRL",
            required=True,
            min_length=5,
            max_length=15,
            custom_id="player_tag"
        )
        
        super().__init__(
            title="Enter In-game Tag",
            components=[self.tag]
        )

    async def on_submit(self, interaction: disnake.ModalInteraction):
        try:
            from .utils import get_coc_player
            
            # Clean and validate player tag
            player_tag = self.tag.value.replace(" ", "").upper().replace("O", "0")
            if not player_tag.startswith("#"):
                player_tag = "#" + player_tag

            # Defer the response immediately
            await interaction.response.defer(ephemeral=True)
            
            # Validate player tag
            player_data = await get_coc_player(player_tag)
            if player_data is None:
                await interaction.followup.send("😓 Invalid player tag. Please check your tag and try again.", ephemeral=True)
                return

            guild = interaction.guild
            user = interaction.user
            
            # Create Discord-safe channel name
            safe_username = ''.join(c for c in user.display_name.lower() if c.isalnum())[:20]
            if not safe_username:
                safe_username = f"user{user.id}"
            channel_name = f"ticket-{safe_username}"
            
            # Check for existing ticket
            existing_ticket = disnake.utils.get(guild.text_channels, name=channel_name)
            if existing_ticket:
                embed = disnake.Embed(
                    description=f"You already have a ticket: {existing_ticket.mention}",
                    color=disnake.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Get staff role
            staff_role = await get_staff_role(guild)
            if not staff_role:
                await interaction.followup.send("Staff role is not configured. Please contact an administrator.", ephemeral=True)
                return

            # Get category
            category_id = await get_category_id()
            category = None
            if category_id:
                try:
                    category = guild.get_channel(int(category_id))
                except (ValueError, TypeError):
                    print(f"Invalid category_id: {category_id}")

                                                  # Set up channel permissions (using correct Disnake permission names)
            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                user: disnake.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True, 
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True,
                    use_external_emojis=True,
                    add_reactions=True
                ),
                staff_role: disnake.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True, 
                    read_message_history=True, 
                    manage_messages=True,
                    attach_files=True,
                    embed_links=True,
                    use_external_emojis=True,
                    add_reactions=True,
                    manage_channels=True
                )
            }

            # Create ticket channel
            ticket_channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                reason=f"Clan application ticket for {user.display_name}"
            )

            # Get welcome embed data
            welcome_embed_data = await get_welcome_embed_data()
            if welcome_embed_data and welcome_embed_data.get("embeds"):
                welcome_embeds = [disnake.Embed.from_dict(e) for e in welcome_embed_data["embeds"]]
                welcome_content = welcome_embed_data.get("content")
            else:
                welcome_embeds = [disnake.Embed(
                    title="🎉 Clan Application Ticket",
                    description=f"Welcome {user.mention}!\n\nYour clan application ticket has been created. Our staff team will review your profile shortly.",
                    color=disnake.Color.green()
                )]
                welcome_content = None

            # Send welcome message with enhanced view
            staff_mention = staff_role.mention
            content_parts = [user.mention, staff_mention]
            if welcome_content:
                content_parts.append(welcome_content)
            
            ticket_message = await ticket_channel.send(
                content=" ".join(content_parts),
                embeds=welcome_embeds,
                view=TicketActionsView(safe_username, staff_role.id, player_data)
            )
            
            # Pin the welcome message
            try:
                await ticket_message.pin()
            except disnake.HTTPException:
                pass  # Ignore if pinning fails

            # Send confirmation to user
            confirm_embed = disnake.Embed(
                title="✅ Ticket Created Successfully!",
                description=f"Your clan application ticket has been created: {ticket_channel.mention}\n\nOur staff team will review your application shortly.",
                color=disnake.Color.green()
            )
            await interaction.followup.send(embed=confirm_embed, ephemeral=True)
            
        except disnake.HTTPException as e:
            print(f"Discord HTTP error creating ticket: {e}")
            await self._send_error_message(interaction, "Discord API error occurred. Please try again.")
        except Exception as e:
            print(f"Error creating ticket: {e}")
            await self._send_error_message(interaction, "An unexpected error occurred. Please try again or contact an administrator.")
    
    async def _send_error_message(self, interaction: disnake.ModalInteraction, message: str):
        """Helper method to send error messages"""
        error_embed = disnake.Embed(
            title="❌ Error",
            description=message,
            color=disnake.Color.red()
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=error_embed, ephemeral=True)
        except:
            pass

class TicketActionsView(disnake.ui.View):
    def __init__(self, username, staff_role_id, player_data):
        super().__init__(timeout=None)
        self.username = username
        self.staff_role_id = staff_role_id
        self.player_data = player_data

    @disnake.ui.button(label="👤 Player Profile", style=disnake.ButtonStyle.primary, custom_id="profile_button")
    async def profile(self, interaction: disnake.MessageInteraction, button: disnake.ui.Button):
        # Create safe username for comparison
        safe_username = ''.join(c for c in interaction.user.display_name.lower() if c.isalnum())[:20]
        if not safe_username:
            safe_username = f"user{interaction.user.id}"
            
        if safe_username != self.username:
            embed = disnake.Embed(
                description="Only the ticket creator can view their profile.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await show_profile(interaction, self.player_data)

    @disnake.ui.button(label="🗑️ Close Ticket", style=disnake.ButtonStyle.danger, custom_id="delete_ticket")
    async def delete_ticket(self, interaction: disnake.MessageInteraction, button: disnake.ui.Button):
        # Check if user has staff role
        staff_role = await get_staff_role(interaction.guild)
        if not staff_role:
            embed = disnake.Embed(
                title="❌ Configuration Error",
                description="Staff role is not configured. Please contact an administrator.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        if staff_role not in interaction.user.roles:
            embed = disnake.Embed(
                title="❌ Permission Denied",
                description="Only staff members can close tickets.",
                color=disnake.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = disnake.Embed(
            title="🗑️ Close Ticket Confirmation",
            description="Are you sure you want to close this ticket? This action cannot be undone.",
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

    @disnake.ui.button(label="✅ Confirm Close", style=disnake.ButtonStyle.danger, custom_id="confirm_delete")
    async def confirm(self, interaction: disnake.MessageInteraction, button: disnake.ui.Button):
        try:
            # Send confirmation message before deleting
            embed = disnake.Embed(
                title="🗑️ Ticket Closing",
                description="This ticket will be closed in 3 seconds...",
                color=disnake.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Add a small delay before deletion
            import asyncio
            await asyncio.sleep(3)
            
            # Delete the channel
            await interaction.channel.delete(reason="Ticket closed by staff")
        except disnake.HTTPException as e:
            print(f"Error deleting ticket channel: {e}")
            # If deletion fails, send error message
            error_embed = disnake.Embed(
                title="❌ Error",
                description="Failed to close the ticket. Please try again or contact an administrator.",
                color=disnake.Color.red()
            )
            try:
                await interaction.followup.send(embed=error_embed, ephemeral=True)
            except:
                pass
    
    @disnake.ui.button(label="❌ Cancel", style=disnake.ButtonStyle.secondary, custom_id="cancel_delete")
    async def cancel(self, interaction: disnake.MessageInteraction, button: disnake.ui.Button):
        embed = disnake.Embed(
            description="Ticket close operation cancelled.",
            color=disnake.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    pass  # No slash commands - all configuration is done via JSON file
