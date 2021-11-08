import pytweet
import os
from typing import Any
from discord.ext import commands


class DisTweetBot(commands.Bot):
    def __init__(self, tweetbot: pytweet.Client, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.twitter = tweetbot

    def run(self, token: str):
        super().run(token)

    async def on_ready(self):
        print(f"Logged In as {self.user} -- {self.user.id}")
        self.session = self.http._HTTPClient__session
        self.load_extension("jishaku")
        self.owner_ids = [685082846993317953, 739443421202087966, 859996173943177226]

        for fn in os.listdir('cogs'):
            try:
                self.load_extension(f"cogs.{fn[:-3]}")
            except:
                print(f"Cannot load extension: {fn}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            err=error.original
            if isinstance(err, pytweet.errors.TooManyRequests):
                await ctx.send("Runtime Error. Return code: 429. Rate limit exceeded!")

            elif isinstance(err, commands.CommandOnCooldown):
                await ctx.message.add_reaction("⏳")

            else:
                await ctx.send(f"Oh no! An error has occured!\n{error}")

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