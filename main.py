import os
import discord
import pytweet
import logging
import random

from constants import HINTS
from bot import DisTweetBot
from helpcommand import CustomHelpCommand
from discord.ext import commands
from discord.commands import Option

logging.getLogger('discord').setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.WARNING)
logging.getLogger('discord.state').setLevel(logging.INFO)
logger = logging.getLogger()

logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
fmt = logging.Formatter('[{asctime}] [{levelname:<7}] {name}: {message}',"%Y-%m-%d %H:%M:%S", style='{')

handler.setFormatter(fmt)
logger.addHandler(handler)

os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_RETAIN'] = 'True'
os.environ['JISHAKU_FORCE_PAGINATOR'] = 'True'
os.environ['JISHAKU_USE_EMBEDS'] = '1'

# pip install git+https://github.com/Pycord-Development/pycord
# pip install git+https://github.com/TheFarGG/PyTweet

twitterbot = pytweet.Client(
    os.environ["bearer_token"],
    consumer_key=os.environ["api_key"],
    consumer_key_secret=os.environ["api_key_secret"],
    access_token=os.environ["access_token"],
    access_token_secret=os.environ["access_token_secret"],
)

bot = DisTweetBot(
    twitterbot,
    command_prefix=commands.when_mentioned_or("e!"),
    help_command=CustomHelpCommand(),
    intents=discord.Intents.all(),
    case_insensitive=True,
    strip_after_prefix=True,
    status=discord.Status.idle,
    activity=discord.Game(name="Follow me on twitter at @TweetyBott!"),
    allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
    owner_ids = [685082846993317953, 739443421202087966],
    dev_ids = [685082846993317953, 739443421202087966, 739443421202087966], #Geno, Sen, Far
    twitter_dev_ids = [1382006704171196419, 1266671761942351872, 1266671761942351872] #Geno, Sen, Far 
)

@bot.after_invoke
async def after_invoke(ctx: commands.Context):
    try:
        bot.db["bot"]["info"]["total_invoked_commands"] += 1
    except KeyError:
        bot.db["bot"] = {"info": {"total_invoked_commands": 50}}

@bot.command(description="Get the bot's ping")
async def ping(ctx: commands.Context):
    await ctx.send(f"PONG! `{round(bot.latency * 1000)}MS`")

@bot.command("info", description="Get the bot info")
async def BotInfo(ctx: commands.Context):
    info = bot.db["bot"]["info"]
    em=discord.Embed(
        title="Bot Information",
        description=f"I invoked **{info['total_invoked_commands']}** total commands with **{len(bot.commands)}** commands registered in my system. A round **{round(len(bot.db.keys()) - 1)}** users logged into my database and I can see a total of **{round(len(bot.users))}** users across **{round(len(bot.guilds))}** guilds.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=em)

#Slash Commands

@bot.slash_command(name="ping", description="Get the bot's ping",
 guild_ids=[858312394236624957]
)
async def _ping(ctx: commands.Context):
    await ctx.respond(f"PONG! `{round(bot.latency * 1000)}MS`")

@bot.slash_command(description="Say hello to me")
async def hello(ctx, name: Option(str, "The name that you want to greet")):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")


token = os.environ["token"]
bot.run(token)