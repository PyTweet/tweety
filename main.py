import os
import discord
import logging

from utils.bot import DisTweetBot
from utils.twitter_bot import twitterbot
from utils.helpcommand import CustomHelpCommand
from discord.ext import commands
from discord.commands import Option


logger = logging.getLogger('pytweet')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='pytweet.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s:%(name)s: %(message)s'))
logger.addHandler(handler)

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_RETAIN"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
os.environ["JISHAKU_USE_EMBEDS"] = "1"

# pip install git+https://github.com/Pycord-Development/pycord
# pip install git+https://github.com/TheFarGG/PyTweet

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
    owner_ids=[
        685082846993317953, #Geno
        859996173943177226, #Far
        687943803604303872  #Other Geno
    ],
    dev_ids=[
        685082846993317953, # Geno 
        859996173943177226, # Far
    ], 
    twitter_dev_ids=[
        1382006704171196419, # Geno
        1439986191424577537, # Far
    ],
)


@bot.after_invoke
async def after_invoke(ctx: commands.Context):
    await bot.meta_db_cursor.execute("UPDATE main SET total_invoked_commands = total_invoked_commands + 1")
    await bot.meta_db.commit()


@bot.command(description="Get the bot's ping")
async def ping(ctx: commands.Context):
    await ctx.send(f"PONG! `{round(bot.latency * 1000)}MS`")


@bot.command(
    "info", 
    description="Gets the bot info"
)
@commands.cooldown(1, 3, commands.BucketType.default)
async def bot_info(ctx: commands.Context):
    data = await (await bot.db_cursor.execute("SELECT * FROM main")).fetchall()
    meta_data = await (await bot.meta_db_cursor.execute("SELECT * FROM main")).fetchone()
    users = len(data)
    
    em = discord.Embed(
        title="Bot Information",
        description=f"I invoked **{meta_data[0]}** total commands with **{len(bot.commands)}** commands registered in my system. A round **{users}** users logged into my database and I can see a total of **{round(len(bot.users))}** users across **{round(len(bot.guilds))}** guilds.",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=em)


# Slash Commands


@bot.slash_command(
    name="ping", 
    description="Gets the bot's latency!"
)
async def _ping(ctx: commands.Context):
    await ctx.respond(f":ping_pong: | {round(bot.latency * 1000)}ms!")


@bot.slash_command(
    name="hello", 
    description="Say hello to me!"
)
async def _hello(ctx, name: Option(str, "The name that you want to greet")):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")

token = os.environ["token"]
bot.run(token)
