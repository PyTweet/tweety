import discord
from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        cmd = [cmd for cog, cmd in mapping.items()]
        em = discord.Embed(
            title="HelpCommand",
            description=f"Hello there, my name in Tweety. I'm a discord bot made using Discord.py and pytweet for twitter commands related. You can make bot with twitter functions like me using [pytweet](https://pypi.org/project/PyTweet/).\n\nList Command: {', '.join([command.qualified_name for command in cmd[0]])}",
            color=discord.Color.blue(),
        ).set_footer(text="You can use e!help <command> for more info about a command")

        await self.context.send(embed=em)

    async def send_command_help(self, command):
        em = discord.Embed(
            title=command.qualified_name,
            description=f"**Description:** {command.description}\n**Usage:** {command.qualified_name + ' ' + command.signature if command.signature else self.context.prefix + command.qualified_name}",
            color=discord.Color.blue(),
        )
        
        await self.context.send(embed=em)
