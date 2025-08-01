import os
from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
import importlib.util
import pathlib

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    activity=discord.Activity(
        type=discord.ActivityType.custom,
        name="🔍 Scouting Bases",
        state="🔍 Scouting Bases"
    ),
    status=discord.Status.online
)

# List all directories you want to load commands from
command_dirs = ["commands"]
for dir_name in command_dirs:
    commands_dir = pathlib.Path(__file__).parent / dir_name
    if not commands_dir.exists():
        continue
    for file in commands_dir.glob("*.py"):
        if file.name.startswith("_"):
            continue
        # Module name includes directory for uniqueness (e.g. ticket.ticket)
        module_name = f"{dir_name}.{file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "setup"):
            module.setup(bot)

@bot.event
async def on_ready():
    from commands.ticket import TicketPanelView
    
    bot.add_view(TicketPanelView())
    await bot.tree.sync()
    
    print(f"Bot ready as {bot.user}")

@bot.event
async def on_message(message):
    # Ignore messages from bots
    if message.author.bot:
        return
    
    # Check if bot is mentioned and message contains "post"
    if bot.user in message.mentions and "post" in message.content.lower():
        # Check if user has admin permissions
        if not message.author.guild_permissions.administrator:
            # Silently ignore - no response
            return
        
        # Parse for channel mentions
        target_channel = None
        if message.channel_mentions:
            target_channel = message.channel_mentions[0]  # Use first mentioned channel
        
        # Send panel
        from commands.ticket import send_panel_to_channel
        await send_panel_to_channel(bot, message, target_channel)
    
    # Process other commands
    await bot.process_commands(message)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("DISCORD_TOKEN is not set properly in your environment variables.")
        exit(1)
    bot.run(DISCORD_TOKEN)
