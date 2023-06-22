import os

from dotenv import load_dotenv
from nextcord import Intents
from nextcord.ext.commands import Bot

load_dotenv()
intents = Intents.all()

bot = Bot(intents=intents)


@bot.event
async def on_ready():
    """"""
    print(f"We have logged in as {bot.user}")


bot.load_extensions(
    [
        # "monitor",
        # "presence",
    ]
)

bot.run(os.getenv("BETA_TOKEN"))


# * invite link
# https://discord.com/api/oauth2/authorize?client_id=1120563143513489448&permissions=1101927803984&scope=bot%20applications.commands
