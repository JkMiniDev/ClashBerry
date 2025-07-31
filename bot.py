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
command_dirs = ["commands", "ticket"]
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
    from ticket.ticket import TicketPanelView
    from ticket.utils import send_ticket_panel
    
    bot.add_view(TicketPanelView())
    await bot.tree.sync()
    
    # Send ticket panel to configured channel
    await send_ticket_panel(bot)
    
    print(f"Bot ready as {bot.user}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("DISCORD_TOKEN is not set properly in your environment variables.")
        exit(1)
    bot.run(DISCORD_TOKEN)
