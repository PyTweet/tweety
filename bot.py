import pytweet
import os
import bba
import discord
from replit import db
from typing import Any, List, Optional
from discord import User
from discord.ext import commands
from webserver import keep_alive
from twitter import TwitterUser, Account

class DisTweetBot(commands.Bot):
    def __init__(self, tweetbot: pytweet.Client, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.load_extension("jishaku")
        self.twitter = tweetbot
        self.dev_ids: Optional[List[int]] = kwargs.get("dev_ids")
        self.bc: bba.Client = bba.Client(os.environ['BBA'])
        self.db = db
        self.__user_accounts_cache = {}
        
    def set_user_credentials(self, ctx: commands.Context):
        try:
            user = self.db[str(ctx.author.id)]
            token = user["token"]
            token_secret = user["token_secret"]
            self.twitter.http.access_token = token
            self.twitter.http.access_token_secret = token_secret
        except KeyError:
            return 0

    def _set_account_user(self):
        if not self.twitter.http.access_token:
            return None

        self._account_user = self.twitter.fetch_user(self.twitter.http.access_token.partition("-")[0])

    async def get_user(self, id: int, ctx: commands.Context) -> Optional[User]:
        user = self._connection.get_user(id)
        try:
            twitter_credential = self.db[str(id)]
        except (ValueError, TypeError, KeyError) as e:
            raise e
        else:
            account = Account(self, self.twitter, twitter_credential)
            user = TwitterUser(user, account)
            if not user:
                raise discord.UserNotFound(id)

            if not user.registered:
                await ctx.send("This command require you to login using `e!login` command!")
                return
                
            return user
    
    @property
    def session(self):
        return self.http._HTTPClient__session

    def run(self, token: str):
        super().run(token)

    def get_ranword(self):
        return self.bc.sentence()

    def calc(self, expression: str, variable: str):
        return self.bc.calc(expression, variable)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.author.id in self.owner_ids or before.author.id in self.owner_ids:
            await self.process_commands(after)

    async def on_ready(self):
        keep_alive()
        print("loading cogs!")
        for fn in os.listdir('cogs'):
            try:
                if not fn == "__pycache__":
                    self.load_extension(f"cogs.{fn[:-3]}")
            except Exception as e:
                print(f"Cannot load extension: {fn}")
                raise e
        print(f"Logged In as {self.user} -- {self.user.id}")

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError):
            err=error.original
            if isinstance(err, pytweet.errors.TooManyRequests):
                await ctx.send("Runtime Error. Return code: 429. Rate limit exceeded!")

            elif isinstance(err, commands.CommandOnCooldown):
                await ctx.message.add_reaction("⏳")

            else:
                await ctx.send(error)
                raise error

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Im on cooldown! Please wait {error.retry_after:.2f} seconds")

        elif isinstance(error, commands.NotOwner):
            await ctx.send(f"Only owner can do that command sus")
            ctx.command.reset_cooldown(ctx)

        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f"Check have failed! You are not in check")

        else:
            try:
                ctx.command.reset_cooldown(ctx)
            except AttributeError:
                pass
                
            raise error