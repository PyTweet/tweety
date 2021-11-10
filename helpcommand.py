import discord
from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    def ctx(self):
        return self.context

    async def send_bot_help(self, mapping):
        commands=""
        for cog, list_commands in mapping.items():
            for cmd in list_commands:
                if cmd.qualified_name != "jishaku":
                    commands += f" {cmd.qualified_name},"

        em = discord.Embed(
            title="HelpCommand",
            description=f"Hello there, my name in Tweety. I'm a discord bot made using PyCord and pytweet for twitter commands related. You can make bot with twitter functions like me using [pytweet](https://pypi.org/project/PyTweet/).\n\nList Command: {commands}",
            color=discord.Color.blue(),
        ).set_footer(text="You can use e!help <command> for more info about a command")

        await self.ctx.send(embed=em)

    async def send_command_help(self, command):
        em = discord.Embed(
            title=command.qualified_name,
            description=f"**Description:** {command.description}\n**Usage:** {command.qualified_name + ' ' + command.signature if command.signature else self.ctx.prefix + command.qualified_name}",
            color=discord.Color.blue(),
        )
        
        await self.ctx.send(embed=em)