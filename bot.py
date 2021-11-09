import pytweet
import os
from typing import Any
from discord.ext import commands
from bba import Client

class DisTweetBot(commands.Bot):
    def __init__(self, tweetbot: pytweet.Client, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.twitter = tweetbot
        self.bc = Client(os.environ['BBA'])

    def run(self, token: str):
        super().run(token)

    def get_ranword(self):
        word = self.bc.sentence()
        return word

    async def on_message_edit(self, before, after):
        if after.author.id in self.owner_ids or before.author.id in self.owner_ids:
            ctx: commands.Context = await self.get_context(after)
            await self.invoke(ctx)

    async def on_ready(self):
        print(f"Logged In as {self.user} -- {self.user.id}")
        self.session = self.http._HTTPClient__session
        self.load_extension("jishaku")

        for fn in os.listdir('cogs'):
            try:
                if not fn == "__pycache__":
                    self.load_extension(f"cogs.{fn[:-3]}")
            except Exception as e:
                print(f"Cannot load extension: {fn}")
                raise e

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            err=error.original
            if isinstance(err, pytweet.errors.TooManyRequests):
                await ctx.send("Runtime Error. Return code: 429. Rate limit exceeded!")

            elif isinstance(err, commands.CommandOnCooldown):
                await ctx.message.add_reaction("⏳")

            else:
                await ctx.send(f"Oh no! An error has occured!\n{error}")
                raise error


        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Im on cooldown! Please wait {error.retry_after:.2f} seconds")

        elif isinstance(error, commands.NotOwner):
            await ctx.send(f"Only owner can do that command sus")
            ctx.command.reset_cooldown(ctx)

        else:
            try:
                ctx.command.reset_cooldown(ctx)
            except AttributeError:
                pass
                
            raise error