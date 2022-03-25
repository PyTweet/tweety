import pytweet
import os
import bba
import discord
import asyncio
import aiosqlite
import datetime

from discord.ext import commands
from typing import Any, List, Optional
from discord import User
from webserver import keep_alive
from twitter import TwitterUser, Account
from objects import DisplayModels, to_dict

class DisTweetBot(commands.Bot):
    def __init__(self, tweetbot: pytweet.Client, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.twitter = tweetbot
        self.dev_ids: Optional[List[int]] = kwargs.get("dev_ids")
        self.twitter_dev_ids: Optional[List[int]] = kwargs.get("twitter_dev_ids")
        self.bc: bba.Client = bba.Client(os.environ["BBA"])
        self.displayer = DisplayModels(self)
        self._uptime = datetime.datetime.utcnow()

    @property
    def uptime(self):
        return self._uptime

    @property
    def session(self):
        return self.http._HTTPClient__session

    async def get_twitter_user(self, id: int, ctx: commands.Context) -> Optional[User]:
        user = self._connection.get_user(id)
        raw_data = await (await self.db.execute("SELECT * FROM main WHERE discord_user_id = ?", (int(id),))).fetchone()

        if not raw_data:
            await ctx.send("This command requires you to login using `e!login` command!")
            return 0

        data = to_dict(raw_data, token=..., token_secret=..., screen_name=..., discord_user_id=..., user_id=...,)
        twitterclient = pytweet.Client(
            os.environ["bearer_token"],
            consumer_key=os.environ["api_key"],
            consumer_secret=os.environ["api_key_secret"],
            access_token=data["token"],
            access_token_secret=data["token_secret"],
        )
        account = Account(self, twitterclient, data)
        Twitteruser = TwitterUser(user, account)
        if not user:
            await ctx.send(
                "This command requires you to login using `e!login` command!"
            )
            return 0

        return Twitteruser

    def run(self, token: str):
        super().run(token)

    def get_ranword(self):
        return self.bc.get_sentence()

    def calc(self, expression: str, variable: str):
        return self.bc.calc(expression, variable)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild:
            return
            
        if before.author.id in self.owner_ids:
            await self.process_commands(after)

    async def on_ready(self):
        self.db = await aiosqlite.connect("db/account.db")
        self.db_cursor = await self.db.cursor()
        self.meta_db = await aiosqlite.connect("db/meta.db")
        self.meta_db_cursor = await self.meta_db.cursor()
        await self.db_cursor.execute(
            """CREATE TABLE IF NOT EXISTS main (
                token TEXT,
                token_secret TEXT,
                screen_name TEXT,
                discord_user_id INTEGER,
                user_id INTEGER
            )"""
        )
        await self.meta_db_cursor.execute(
            """CREATE TABLE IF NOT EXISTS main (
                total_invoked_commands INTEGER
            )"""
        )
        await self.db.commit()
        await self.meta_db.commit()
        keep_alive()

        for fn in os.listdir("cogs"):
            try:
                if not fn == "__pycache__":
                    self.load_extension(f"cogs.{fn[:-3]}")
            except Exception as e:
                print(f"Cannot load extension: {fn} - {e}")
        self.load_extension("jishaku")
        print("Cogs loaded!")
        
        try:
            channel_id = os.environ["shutdown_channel_id"]
        except KeyError:
            channel_id = None
            
        if channel_id:
            channel = self.get_channel(int(channel_id))
            if channel:
                await channel.send("Shutdown completed, I am now online ready to use!")
            os.environ["shutdown_channel_id"] = ""

        print(f"Logged In as {self.user} -- {self.user.id}")

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        try:
            ctx.command.reset_cooldown(ctx)
        except AttributeError as e:
            print(e)
                
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
                await ctx.send("Unauthorized to view resources! There's a chance that the user is protected.")

            elif isinstance(og_error, pytweet.ResourceNotFound):
                await ctx.send("Resource not found! check your spelling.")

            elif isinstance(og_error, pytweet.Unauthorized):
                await ctx.send("You have declined your APP Session! Tweety can no longer do action on behalf of you!")

            elif isinstance(og_error, pytweet.Forbidden):
                await ctx.send(of)

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
            await ctx.send(
                "Unknown error has occured! I will notify my developers! You can use others command and wait until this one is fix ;)"
            )
            raise error