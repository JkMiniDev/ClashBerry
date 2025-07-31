import os
from dotenv import load_dotenv
load_dotenv()
import disnake
from disnake.ext import commands
import importlib.util
import pathlib

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = disnake.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    activity=disnake.Activity(
        type=disnake.ActivityType.custom,
        name="🎫 Managing Tickets",
        state="🎫 Managing Tickets"
    ),
    status=disnake.Status.online
)

# Load commands from commands directory (ticket bot)
command_dirs = ["commands"]
for dir_name in command_dirs:
    commands_dir = pathlib.Path(__file__).parent / dir_name
    if not commands_dir.exists():
        continue
    for file in commands_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
        # Module name includes directory for uniqueness (e.g. commands.ticket)
        module_name = f"{dir_name}.{file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "setup"):
            module.setup(bot)

@bot.event
async def on_ready():
    from commands.ticket import TicketPanelView, TicketControlsView
    from commands.utils import load_config, create_embed_from_data, get_panel_embed_data
    
    # Add persistent views
    bot.add_view(TicketPanelView())
    bot.add_view(TicketControlsView())
    
    print(f"Ticket Bot ready as {bot.user}")
    
    # Auto-post ticket panel
    config = load_config()
    if not config:
        print("❌ No configuration found. Please set up config.json")
        return
        
    server_id = config.get("server_id")
    ticket_channel_id = config.get("ticket_channel_id")
    
    if not server_id or not ticket_channel_id:
        print("❌ Server ID or ticket channel ID not configured")
        return
        
    try:
        # Get the server and channel
        guild = bot.get_guild(int(server_id))
        if not guild:
            print(f"❌ Could not find server with ID: {server_id}")
            return
            
        channel = guild.get_channel(int(ticket_channel_id))
        if not channel:
            print(f"❌ Could not find channel with ID: {ticket_channel_id}")
            return
            
        # Create panel embed
        panel_embed_data = await get_panel_embed_data()
        if panel_embed_data:
            panel_embed = create_embed_from_data(panel_embed_data)
        else:
            # Default panel embed
            panel_embed = disnake.Embed(
                title="🎫 Support Tickets",
                description="Need help? Click the button below to create a support ticket!",
                color=disnake.Color.blue()
            )
        
        # Create and send the ticket panel
        panel_view = TicketPanelView()
        
        # Clear previous messages (optional - remove if you want to keep history)
        try:
            async for message in channel.history(limit=10):
                if message.author == bot.user:
                    await message.delete()
        except:
            pass  # Ignore permission errors
        
        await channel.send(embed=panel_embed, view=panel_view)
        print(f"✅ Ticket panel posted to #{channel.name} in {guild.name}")
        
    except Exception as e:
        print(f"❌ Error posting ticket panel: {e}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("DISCORD_TOKEN is not set properly in your environment variables.")
        exit(1)
    bot.run(DISCORD_TOKEN)
