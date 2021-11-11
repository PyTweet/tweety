from discord.ext import commands

class PostFlag(commands.FlagConverter):
    method: str
    text: str = "tweet tweet"
    tweet_id: str = ''