import pytweet
from typing import Any
from discord.ext import commands


class DisTweetBot(commands.Bot):
    def __init__(self, tweetbot: pytweet.Client, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.twitter=tweetbot

    async def on_ready(self):
        print(f"Log In as {self.twitter.user.username} -- {self.twitter.user.id}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            err=error.original
            if isinstance(err, pytweet.errors.TooManyRequests):
                await ctx.send("Runtime Error. Return code: 429. Rate limit exceeded!")

            else:
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