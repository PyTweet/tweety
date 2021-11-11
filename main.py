import os
import discord
import pytweet
from bot import DisTweetBot
from helpcommand import CustomHelpCommand
from discord.ext import commands
from discord.commands import Option

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
    owner_ids = [685082846993317953],
    dev_ids = [685082846993317953, 907675082019733525, 859996173943177226] #Geno, Far, Sen.
)

@bot.command(description="Get the bot's ping")
async def ping(ctx: commands.Context):
    await ctx.send(f"PONG! `{round(bot.latency * 1000)}MS`")

#Slash Commands
@bot.slash_command(description="Say hello to me")
async def hello(ctx, name: Option(str, "The name that you want to greet")):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")


os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_RETAIN'] = 'True'
os.environ['JISHAKU_FORCE_PAGINATOR'] = 'True'

token = os.environ["token"]
bot.run(token)





