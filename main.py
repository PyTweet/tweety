import os
import discord
import pytweet
from replit import db
from bot import DisTweetBot
from helpcommand import CustomHelpCommand
from discord.ext import commands
from discord.commands import Option
import logging

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
    #allowed_mentions=discord.AllowedMentions(roles=False, everyone=False, users=True),
    owner_ids = [685082846993317953, 739443421202087966],
    dev_ids = [685082846993317953, 739443421202087966] #Geno, Sen.
)

@bot.command(description="Get the bot's ping")
async def ping(ctx: commands.Context):
    await ctx.send(f"PONG! `{round(bot.latency * 1000)}MS`")

@bot.after_invoke
async def after_invoke(ctx):
    print(1)
    bot.twitter.http.access_token = os.environ["access_token"]
    bot.twitter.http.access_token_secret = os.environ["access_token_secret"] 

@bot.slash_command(description="Get the bot's ping",
 guild_ids=[858312394236624957]
)
async def _ping(ctx):
    await ctx.respond(f"PONG! `{round(bot.latency * 1000)}MS`")


#Slash Commands
@bot.slash_command(description="Say hello to me")
async def hello(ctx, name: Option(str, "The name that you want to greet")):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")


token = os.environ["token"]
bot.run(token)





