import pytweet
import os
import bba
import discord
import asyncio
from discord.ext import commands
from replit import db
from typing import Any, List, Optional
from discord import User
from webserver import keep_alive
from twitter import TwitterUser, Account
from objects import DisplayModels


class DisTweetBot(commands.Bot):
    def __init__(self, tweetbot: pytweet.Client, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.load_extension("jishaku")
        self.twitter = tweetbot
        self.dev_ids: Optional[List[int]] = kwargs.get("dev_ids")
        self.twitter_dev_ids: Optional[List[int]] = kwargs.get("twitter_dev_ids")
        self.bc: bba.Client = bba.Client(os.environ["BBA"])
        self.db = db
        self.displayer = DisplayModels(self)

    async def get_twitter_user(self, id: int, ctx: commands.Context) -> Optional[User]:
        user = self._connection.get_user(id)
        try:
            twitter_credential = self.db[str(id)]
        except (ValueError, TypeError, KeyError):
            await ctx.send("This command requires you to login using `e!login` command!")
            return 0

        else:
            twitterclient = pytweet.Client(
                os.environ["bearer_token"],
                consumer_key=os.environ["api_key"],
                consumer_secret=os.environ["api_key_secret"],
                access_token=twitter_credential["token"],
                access_token_secret=twitter_credential["token_secret"],
            )
            account = Account(self, twitterclient, twitter_credential)
            Twitteruser = TwitterUser(user, account)
            if not user:
                await ctx.send(
                    "This command requires you to login using `e!login` command!"
                )
                return 0

            return Twitteruser

    @property
    def session(self):
        return self.http._HTTPClient__session

    def run(self, token: str):
        super().run(token)

    def get_ranword(self):
        return self.bc.get_sentence()

    def calc(self, expression: str, variable: str):
        return self.bc.calc(expression, variable)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.id in self.owner_ids and before.guild.id == 858312394236624957):
            await self.process_commands(after)

    async def on_ready(self):
        keep_alive()
        
        try:
            channel_id = os.environ["shutdown_channel_id"]
        except KeyError:
            channel_id = None
            
        if channel_id:
            channel = self.get_channel(int(channel_id))
            await channel.send("Shutdown completed, I am now online ready to use!")
            os.environ["shutdown_channel_id"] = ""
            
        print("loading cogs!")
        for fn in os.listdir("cogs"):
            try:
                if not fn == "__pycache__":
                    self.load_extension(f"cogs.{fn[:-3]}")
            except Exception as e:
                print(f"Cannot load extension: {fn}")
                raise e

        print(f"Logged In as {self.user} -- {self.user.id}")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandInvokeError):
            og_error = error.original
            if isinstance(og_error, pytweet.errors.TooManyRequests):
                await ctx.send("Rate limit exceeded!")

            elif isinstance(og_error, asyncio.TimeoutError):
                await ctx.author.send("You took too long to respond! aborting...")

            elif isinstance(og_error, pytweet.BadRequests):
                await ctx.send(
                    "BadArgument! Arguments that you passed is violating twitter's api rules, Please send a correct argument next time!"
                )
                return

            elif isinstance(og_error, pytweet.UnauthorizedForResource):
                await ctx.send(
                    "Unauthorized to view resources! There's a chance that the user is protected.")

            else:
                await ctx.send(
                    "Unknown error has occured! I will notify my developers! You can use others command and wait until this one is fix ;)"
                )
                raise og_error

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"Im on cooldown! Please wait {error.retry_after:.2f} seconds",
                delete_after=error.retry_after,
            )

        elif isinstance(error, commands.NotOwner):
            await ctx.send(f"Only owner can do that command!")
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"Check have failed! You are not in check")

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)

        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(error)

        else:
            try:
                ctx.command.reset_cooldown(ctx)
            except AttributeError:
                pass

            await ctx.send(
                "Unknown error has occured! I will notify my developers! You can use others command and wait until this one is fix ;)"
            )
            raise error
