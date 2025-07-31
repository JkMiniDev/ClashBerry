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
    from commands.ticket import TicketPanelView
    bot.add_view(TicketPanelView())
    print(f"Ticket Bot ready as {bot.user}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("DISCORD_TOKEN is not set properly in your environment variables.")
        exit(1)
    bot.run(DISCORD_TOKEN)
