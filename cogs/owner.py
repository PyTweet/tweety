import requests
import sys
import os
from discord.ext import commands

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("say", description="Use this command to make the bot say something in the invoked channel.")
    @commands.is_owner()
    async def _bot_say(self, ctx, *,word):
        await ctx.message.delete()
        await ctx.send(word)

    @commands.command("download", description="Download an image/video/gif to a folder")
    @commands.is_owner()
    async def download(self, ctx, url, filename):
        r = requests.get(url, allow_redirects=True)
        with open(f"media/{filename}", "wb") as fn:
            fn.write(r.content)
        await ctx.send("Done! Img saved in images folder.")

    @commands.command("restart", aliases=["shutdown"], escription="Restart the bot")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.reply('Restarting... If I don\'t comeback in the next 20 seconds then am dead')
        os.environ["shutdown_channel_id"] = str(ctx.channel.id)

        python = sys.executable
        os.execl(python, python, * sys.argv)

def setup(bot):
    bot.add_cog(Owner(bot))