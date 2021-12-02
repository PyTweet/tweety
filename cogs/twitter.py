import discord
import pytweet
import os
from discord.ext import commands
from typing import Union
from views import Paginator
from discord.ui import Button, View, Select



def to_keycap(c):
    return '\N{KEYCAP TEN}' if c == 10 else str(c) + '\u20e3'

def is_developer():
    def predicate(ctx: commands.Context):
        if ctx.author.id in ctx.bot.dev_ids or ctx.author.id in ctx.bot.owner_ids:
           return True
        return False
    return commands.check(predicate)

class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("login", description="Create a set of user access token so you can use twitter related commands in with your account!")
    async def LogIn(self, ctx: commands.Context):
        self.bot.twitter.http.access_token = os.environ["access_token"]
        self.bot.twitter.http.access_token_secret = os.environ["access_token_secret"] #To be sure its TweetyBott
        try:
            self.bot.db[str(ctx.author.id)]
        except KeyError:
            pass
        else:
            try:
                db = self.bot.db[str(ctx.author.id)]
                await ctx.send(f"You are were already logged in as: `{db['screen_name']}` with id `{db['user_id']}`")
                return
            except KeyError:
                user = await self.bot.get_user(ctx.author.id, ctx)
                if not user:
                    return

                await ctx.send(f"You are were already logged in as: `{user.twitter_account.username}` with id `{user.twitter_account.id}`")
                db = self.bot.db[str(ctx.author.id)]
                db["screen_name"] = user.twitter_account.username
                db["user_id"] = user.twitter_account.id
                return

        oauth = pytweet.OauthSession.with_oauth_flow(self.bot.twitter)
        await ctx.send("Follow my instruction to register your account to my database!\n1. I will send a url to your dm, click it.\n2. after that you have to authorize TweetyBott application, then you will get redirect to `https://twitter.com`, the url contain an access token & secret.\n3. Copy the website url and send it to my dm.")
        link = oauth.generate_oauth_url("direct_messages")
        await ctx.author.send(f"**Step 1 & 2**\nClick & Authorize TweetBott in this url --> {link}")
        
        def check(msg):
            return msg.guild is None and msg.author.id != self.bot.user.id

        await ctx.author.send("**Step 3**\n Send me the redirect url link! you have a minute to do this!")
        msg = await self.bot.wait_for("message", timeout = 60*5, check=check)
        await ctx.author.send(f"Got the url ||`{msg.content}`|| ! please wait for couple of seconds!")
        if not "oauth_token=" in msg.content and not "oauth_verifier=" in msg.content:
            await ctx.author.send("Wrong url sent! use `e!login` command again and make sure you put the right url!")
            return

        domain, url = msg.content.split("?")
        raw_oauth_token, raw_oauth_verifier = url.split("&")
        oauth_token_credential, oauth_token = raw_oauth_token.split("=")
        oauth_verifier_credential, oauth_verifier = raw_oauth_verifier.split("=")
        oauth_token, oauth_token_secret, user_id, screen_name = oauth.post_oauth_token(oauth_token, oauth_verifier)

        oauth_token_credential, oauth_token = oauth_token.split("=")
        oauth_verifier_credential, oauth_secret = oauth_token_secret.split("=")
        user_id_credential, user_id = user_id.split("=")
        screen_name_credential, screen_name = screen_name.split("=")

        data = {"token": oauth_token, "token_secret": oauth_secret, "screen_name": "@" + screen_name, "user_id": user_id}
        self.bot.db[str(ctx.author.id)] = data
        await ctx.author.send(f"Done, You are logged as `{screen_name}` with id `{user_id}`")
        await ctx.send(f"{ctx.author.mention} --- Now you can use twitter related commands, please check `e!help` for twitter related commands or you can start with `e!post - Post test from @TweetBott`. Note that if you want to declined my connection, you can revoke it by going to <https://twitter.com/settings/apps_and_sessions>. **Note that you CANNOT use twitter related command anymore after this!**")

    @commands.command("logout", description="Logout from your current twitter account, mean the data in my database will get delete and will be invalid!")
    async def LogOut(self, ctx: commands.Context):
        yes = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        no = discord.ui.Button(label="NO", style=discord.ButtonStyle.red)

        async def yes_callback(interaction):
            no.disabled = True
            yes.disabled = True
            del self.bot.db[str(interaction.user.id)]
            await ctx.send("Logged out! If you want to use twitter commands, you can use `e!login` again")
            
        async def no_callback(interaction):
            no.disabled = True
            yes.disabled = True
            await interaction.response.edit_message("Exit command!")
            await msg.edit(view = view)
            return

        yes.callback = yes_callback
        no.callback = no_callback
        view = discord.ui.View()
        view.add_item(yes)
        view.add_item(no)

        msg = await ctx.send("Are you sure you want to logout your account?", view=view)

    @commands.command('user', description="A command for user lookup, can be use by anyone!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def userLookup(self, ctx: commands.Context, username: Union[str, int] = None):
        client = (await self.bot.get_user(ctx.author.id, ctx)).twitter_account.client
        if not client:
            client = self.bot.twitter


        if not username:
            await self.clientAccount(ctx)
            return

        if username.isdigit():
            user = client.fetch_user(username)
        
        else:
            user = client.fetch_user_by_name(username)

        if not user:
            await ctx.send(f"Could not find username with username(or id): [{username}].")
            return

        await self.bot.displayer.display_user(ctx, user)

    @commands.command('tweet', description="A command for tweet lookup, can be use by anyone!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def tweetLookup(self, ctx: commands.Context, tweet_id: int = 1465231032760684548):
        client = await self.bot.get_user(ctx.author.id, ctx)
        if not client:
            return

        tweet = client.twitter_account.client.fetch_tweet(tweet_id)
        if not tweet:
            await ctx.send("That tweet id is not exist!")

        await self.bot.displayer.display_tweet(ctx, tweet, None)

    @commands.command("following", aliases=["followings"], description="Return users that you followed, can be use by anyone!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def Clientfollowing(self, ctx: commands.Context):
        client = await self.bot.get_user(ctx.author.id, ctx)
        if not client:
            return

        paginator = commands.Paginator(prefix = "", suffix = "", max_size = 370)
        user =  client.twitter_account
        try:
            users = user.fetch_following()
            if not users:
                await ctx.send(f"{user.username} Your havent followed anyone!")
                return

            for num, user in enumerate(users):
                paginator.add_line(f"{num + 1}. {user.username}({user.id})")
            
            
        except TypeError:
            await ctx.send(f"{user.username} You havent followed anyone!")
            return

        else:
            em = discord.Embed(
                title=f"Total of {len(users)} users!",
                description="",
                color=discord.Color.blue(),
            ).set_author(
                name=f"Viewing {user.username}'s following",
                icon_url=user.profile_url
            )
            em.description = paginator.pages[0]
            paginator = Paginator(paginator, ctx.author, embed = em)
            await ctx.send(embed = em, view =paginator)

    @commands.command("account", aliases=["profile", "acc"], description="See your account! This command require you to login using `e!login` command!")
    async def clientAccount(self, ctx):
        me = await self.bot.get_user(ctx.author.id, ctx)
        if not me:
            return

        id = me.twitter_account.user_id
        if not id:
            id = me.twitter_account.id
            self.bot.db[str(ctx.author.id)]["user_id"] = id #Store the id in the database if it was not in the database, this is use to avoid ratelimit!

        await self.userLookup(ctx, str(id))

    @commands.command("follower", aliases=["followers"], description="Return users that you followed, can be use by anyone!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def Clientfollower(self, ctx: commands.Context):
        client = await self.bot.get_user(ctx.author.id, ctx)
        if not client:
            return

        paginator = commands.Paginator(prefix = "", suffix = "", max_size = 370)
        user = client.twitter_account
        try:
            users = user.fetch_followers()
            if not users:
                await ctx.send(f"{user.username} You done have a follower :pensive: !")
                return

            for num, user in enumerate(users):
                paginator.add_line(f"{num + 1}. {user.username}({user.id})")
            
            
        except TypeError:
            await ctx.send(f"{user.username} You done have a follower :pensive: !")
            return

        else:
            em = discord.Embed(
                title=f"Total of {len(users)} users!",
                description="",
                color=discord.Color.blue(),
            ).set_author(
                name=f"Viewing {ctx.author.name}'s followers",
                icon_url=ctx.author.avatar.url
            )
            em.description = paginator.pages[0]
            paginator = Paginator(paginator, ctx.author, embed = em)
            await ctx.send(embed = em, view =paginator)

    @commands.command("follow",description="Follow a user, require you to login using `e!login` command!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def followUser(self, ctx: commands.Context, username: str):
        client = await self.bot.get_user(ctx.author.id, ctx)
        if not client:
            return

        user = None
        me = client.twitter_account
        if username.isdigit():
            user = client.twitter_account.client.fetch_user(int(username))

        else:
            user = client.twitter_account.client.fetch_user_by_name(username)

        if not user:
            await ctx.send("Username/id is not exist!")
            return

        user.follow()
        await ctx.send(f"{me.username} Has followed {user.username}!")

    @commands.command("unfollow", description="UnFollow a user, require you to login using `e!login` command!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def unfollowUser(self, ctx: commands.Context, username: str):
        client = await self.bot.get_user(ctx.author.id, ctx)
        if not client:
            return

        user = None
        me = client.twitter_account
        if username.isdigit():
            user = client.twitter_account.client.fetch_user(int(username))

        else:
            user = client.twitter_account.client.fetch_user_by_name(username)

        if not user:
            await ctx.send("Username/id is not exist!")
            return

        user.unfollow()
        await ctx.send(f"{me.username} Has unfollowed {user.username}!")

    @commands.command("send", description="Send a message to a user, require you to login using `e!login` command!")
    @commands.is_owner()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def sendMessagetoUser(self, ctx: commands.Context, username: Union[str, int], *, text: str):
        user = None
        client = await self.bot.get_user(ctx.author.id, ctx)
        if not client:
            return


        if username.isdigit():
            user = client.twitter_account.client.fetch_user(int(username))

        else:
            user = client.twitter_account.client.fetch_user_by_name(username)

        if not user:
            await ctx.send("Username/id is not exist!")
            return

        user.send(text)
        await ctx.send(f"Send message to {user.username}")

    @commands.command("post", description="Post a tweet to twitter! require you to login using `e!login` command!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def postTweet(self, ctx: commands.Context, flag: str, *, text=None):
        tweet=None
        user = await self.bot.get_user(ctx.author.id, ctx)
        if not user:
            return

        try:
            if flag.lower() in ("-random", "-ran"):
                word = self.bot.get_ranword()
                tweet = user.twitter_account.client.tweet(word.response)
                await ctx.send(f"Posted! check it on https://twitter.com/TweetyBott/status/{tweet.id}")

            elif flag.lower() in ("-reply", "-re", "-r", "-rep"):
                text=text.split(" ")
                tweet_id = text[0]
                msg = ''
                for word in text[1:]:
                    if word != text[-1]:
                        msg += f"{word} "
                    else: 
                        msg += word

                tweet = user.twitter_account.client.tweet(msg, reply_tweet = tweet_id)
                await ctx.send(f"Reply complete! check it on https://twitter.com/TweetyBott/status/{tweet.id}")

            elif flag.lower() in ("-q", "-quo", "-quote"):
                text=text.split(" ")
                tweet_id = text[0]
                msg = ''
                for word in text[1:]:
                    if word != text[-1]:
                        msg += f"{word} "
                    else: 
                        msg += word
                        
                tweet = user.twitter_account.client.tweet(msg, quote_tweet = tweet_id)
                await ctx.send(f"Quote complete! check it on https://twitter.com/TweetyBott/status/{tweet.id}")

            elif flag.lower() in ("-", "-none", "--"):
                tweet = user.twitter_account.client.tweet(text)
                await ctx.send(f"Posted! check it on https://twitter.com/TweetyBott/status/{tweet.id}")

            else:
                await ctx.send(f"Unknown flags parsed: {flag}\n**How Do I Post A Tweet?**\n`1.` Make sure you are login and register your account in tweetybot, use `e!login` if you haven't.\n`2.` Specified which flag you want to use, (e.g): `-reply` is use to reply a tweet, `-random` is use to post random content in a tweet, `- or -none` is use to post normal tweet and `-quote` is for quoting a tweet.\n`3.` Invoke the command, here's examples:\n**`A.`** Normal Post = `e!post - your_message`\n**`B.`** Reply Post = `e!post -replay Tweet_id your_message`\n**`C.`** Random Post = `e!post -random`\n**`D.`** Quote Tweet = `e!post -quote Tweet_id your_message`")

        except Exception as e:
            if isinstance(e, pytweet.Forbidden):
                await ctx.send(f"Posted! check it on https://twitter.com/TweetyBott/status/{tweet.id}")
                await ctx.send(f"Also it return this:\n{e}")

            elif isinstance(e, KeyError):
                await ctx.send("You are not login! use `e!login` command!")

            elif isinstance(e, AttributeError):
                await ctx.send(f"Could not find tweet with id: [{id}].")

            elif isinstance(e, pytweet.Unauthorized):
                await ctx.send("You have declined your APP Session! Tweety can no longer do action on behalf of you!")

            else:
                raise e

    @commands.command("reply", description="Reply to a tweet, require you to login using `e!login` command!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def replyTweet(self, ctx: commands.Context, tweet_id: int, *,text):
        user = await self.bot.get_user(ctx.author.id, ctx)
        if not user:
            return

        tweet = user.twitter_account.client.tweet(text, reply_tweet = tweet_id)
        await ctx.send(f"Posted! check it on https://twitter.com/{user.twitter_account.username.replace('@', '')}/status/{tweet.id}")
            

def setup(bot: commands.Bot):
    bot.add_cog(Twitter(bot))