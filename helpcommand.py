import discord
from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        cmd = [cmd for cog, cmd in mapping.items()]
        em = discord.Embed(
            title="HelpCommand",
            description=f"Hello there, my name in Entharryno. I'm a discord bot made using PyCord, and pytweet for twitter commands. You can make bot like me using [pytweet](https://pypi.org/project/PyTweet/).\n\nList Command: {', '.join([command.qualified_name for command in cmd[0]])}",
            color=discord.Color.blue(),
        ).set_footer(text="You can use e!help <command> for mor info about a command")

        await self.context.send(embed=em)
