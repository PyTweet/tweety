import discord
import pytweet
from discord.ext import commands
from typing import Union

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
        try:
            self.bot.db[str(ctx.author.id)]
        except KeyError:
            pass
        else:
            await ctx.send("You already login!")
            return

        oauth = pytweet.OauthSession.with_oauth_flow(self.bot.twitter)
        await ctx.send("Follow my instruction to register your account to my database!\n1. I will send a url to your dm, click it.\n2. after that you have to authorize TweetyBott application, then you will get redirect to `https://twitter.com`, the url contain an access token & secret.\n3. Copy the website url and send it to my dm.")
        link = oauth.generate_oauth_url()
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
        oauth_token, oauth_token_secret, user_id, screen_name = oauth.post_access_token(oauth_token, oauth_verifier)

        oauth_token_credential, oauth_token = oauth_token.split("=")
        oauth_verifier_credential, oauth_secret = oauth_token_secret.split("=")
        user_id_credential, user_id = user_id.split("=")
        screen_name_credential, screen_name = screen_name.split("=")

        data = {"token": oauth_token, "token_secret": oauth_secret}
        self.bot.db[str(ctx.author.id)] = data
        await ctx.author.send(f"Done, You are logged as `{screen_name}` with id `{user_id}`")
        await ctx.send(f"{ctx.author.mention} --- Now you can use twitter related commands, please check `e!help` for twitter related commands or you can start with `e!post - Post test from @TweetBott`. Note that if you want to declined my connection, you can revoke it by going to <https://twitter.com/settings/apps_and_sessions>. **Note that you CANNOT use twitter related command anymore after this!**")

    @commands.command("logout", description="Logout from your current twitter account, mean the data in my database will get delete!")
    async def LogOut(self, ctx: commands.Context):
        await ctx.send("Ask my dev to complete this command :neutral:")

    @commands.command('user', description="A command for user lookup, can be use by anyone!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def userLookup(self, ctx: commands.Context, username: Union[str, int]):
        try:
            user=None

            if username.isdigit():
                user=self.bot.twitter.fetch_user(username)
            
            else:
                user = self.bot.twitter.fetch_user_by_name(username)
            await ctx.send(
                embed=discord.Embed(
                    title=user.name,
                    url=user.profile_link,
                    description=f":link: {user.link if len(user.link) > 0 else '*This user doesnt provide link*'} • <:compas:879722735377469461> {user.location}\n\n{user.bio if len(user.bio) > 0 else '*User doesnt provide a bio*'}",
                    color=discord.Color.blue(),
                )
                .set_author(
                    name=user.username + f"({user.id})",
                    icon_url=user.avatar_url,
                    url=user.profile_link,
                )
                .set_footer(
                    text=f"Created Time: {user.created_at.strftime('%Y/%m/%d')}",
                    icon_url=user.avatar_url,
                )
                .add_field(
                    name="Followers",
                    value=user.follower_count
                )
                .add_field(
                    name="Following",
                    value=user.following_count
                )
                .add_field(
                    name="Tweets",
                    value=user.tweet_count
                )
                .add_field(
                    name="Listed",
                    value=user.listed_count
                )
            )

        except pytweet.errors.NotFoundError:
            await ctx.send(f"Could not find user with username(or id): [{username}].")

    @commands.command('tweet', description="A command for tweet lookup, can be use by anyone!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def tweetLookup(self, ctx: commands.Context, tweet_id: int):
        try:
            tweet = self.bot.twitter.fetch_tweet(tweet_id)
            user = tweet.author
            em=discord.Embed(
                title=f"Posted by {user.name}",
                url=tweet.link,
                description=tweet.text,
                color=discord.Color.blue()
            ).set_author(
                name=user.username + f"({user.id})",
                icon_url=user.avatar_url,
                url=user.profile_link
            ).set_footer(
                text=f"{tweet.like_count}👍 {tweet.retweet_count}📰 {tweet.reply_count}🗨️",
                icon_url=user.avatar_url
            ).add_field(
                name="Tweet Date", 
                value=tweet.created_at.strftime('%Y/%m/%d')
            ).add_field(
                name="Source", 
                value=tweet.source
            ).add_field(
                name="Reply setting", 
                value=tweet.raw_reply_setting
            )
        

            if tweet.embeds:
                em.set_image(
                    url=tweet.embeds[0]
                )

            await ctx.send(
                embed=em
            )

            if tweet.poll:
                await ctx.send(
                    "looks like this tweet has a poll, mind checking that out with `e!poll <tweet_id>`?"
                )

        except pytweet.errors.NotFoundError:
            await ctx.send(f"Could not find tweet id: [{tweet_id}].")

    @commands.command("following", description="Return users that you followed, can be use by anyone!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def Clientfollowing(self, ctx: commands.Context):
        txt=""
        error_code = self.bot.set_user_credentials(ctx)
        if error_code == 0:
            await ctx.send("Cannot do interaction, you are not login, Please use `e!login` command to register your account in my database!")
            return

        if self.bot.twitter.http.access_token != self.bot.twitter.account.id:
            self.bot._set_account_user()
        
        users = self.bot.twitter.account.fetch_following()
        for num, user in enumerate(users):
            txt += f"{num + 1}. {user.username}({user.id})\n"
        await ctx.send(f"Here are **{len(users)}** cool people you followed!\n```yaml\n{txt}```")

    @commands.command("follow",description="Follow a user, require you to login using `e!login` command!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def followUser(self, ctx: commands.Context, username: str):
        error_code = self.bot.set_user_credentials(ctx)
        if error_code == 0:
            await ctx.send("Cannot do interaction, you are not login, Please use `e!login` command to register your account in my database!")
            return

        if self.bot.twitter.http.access_token != self.bot.twitter.account.id:
            self.bot._set_account_user()
            
        try:
            user = None
            me = self.bot.twitter.account
            if username.isdigit():
                user = self.bot.twitter.fetch_user(int(username))

            else:
                user = self.bot.twitter.fetch_user_by_name(username)

            user.follow()
            await ctx.send(f"{me.username} Has followed {user.username}!")

        except Exception as error:
            if isinstance(error, pytweet.errors.NotFoundError):
                await ctx.send(f"Could not find user with username(or id): [{username}].")
            else:
                raise error

    @commands.command("unfollow", description="UnFollow a user, require you to login using `e!login` command!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def unfollowUser(self, ctx: commands.Context, username: str):
        error_code = self.bot.set_user_credentials(ctx)
        if error_code == 0:
            await ctx.send("Cannot do interaction, you are not login, Please use `e!login` command to register your account in my database!")
            return
        self.bot._set_account_user()

        try:
            user = None
            me = self.bot.twitter.account
            if username.isdigit():
                user = self.bot.twitter.fetch_user(int(username))

            else:
                user = self.bot.twitter.fetch_user_by_name(username)

            user.unfollow()
            await ctx.send(f"{me.username} Has unfollowed {user.username}!")

        except Exception as error:
            if isinstance(error, pytweet.errors.NotFoundError):
                await ctx.send(f"Could not find user with username(or id): [{username}].")
                
            else:
                raise error

    @commands.command("send", description="Send a message to a user, require you to login using `e!login` command!")
    @commands.is_owner()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def sendMessagetoUser(self, ctx: commands.Context, username: Union[str, int], *, text: str):
        user = None
        error_code = self.bot.set_user_credentials(ctx)
        if error_code == 0:
            await ctx.send("Cannot do interaction, you are not login, Please use `e!login` command to register your account in my database!")
            return

        if username.isdigit():
            user = self.bot.twitter.fetch_user(int(username))

        else:
            user = self.bot.twitter.fetch_user_by_name(username)

        user.send(text)
        await ctx.send(f"Send message to {user.username}")

    @commands.command("post", description="Post a tweet to twitter! require you to login using `e!login` command!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def postTweet(self, ctx: commands.Context, flag: str, *, text=None):
        tweet=None
        error_code = self.bot.set_user_credentials(ctx)
        if error_code == 0:
            await ctx.send("Cannot do interaction, you are not login, Please use `e!login` command to register your account in my database!")
            return 

        try:
            if flag.lower() in ("-random", "-ran"):
                word = self.bot.get_ranword()
                tweet = self.bot.twitter.tweet(word.response)
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

                await ctx.send(f"e!post {tweet_id} {msg}")
                tweet=self.bot.twitter.tweet(msg, reply_tweet = tweet_id)
                await ctx.send(f"Reply complete! check it on https://twitter.com/TweetyBott/status/{tweet.id}")

            elif flag.lower() in ("-", "-none", "--"):
                tweet=self.bot.twitter.tweet(text)
                await ctx.send(f"Posted! check it on https://twitter.com/TweetyBott/status/{tweet.id}")

            else:
                await ctx.send(f"Unknown flags parsed: {flag}\n**How Do I Post A Tweet?**\n`1.` Make sure you are login and register your account in tweetybot, use `e!login` if you haven't.\n`2.` Specified which flag you want to use, (e.g): `-reply` is use to reply a tweet, `-random` is use to post random content in a tweet, `- or -none` is use to post normal tweet.\n`3.` Invoke the command, here's examples:\n**`A.`** Normal Post = `e!post - your_message`\n**`B.`** Reply Post = `e!post -replay Tweet_id your_message`\n**`C.`** Random Post = `e!post -random`")

        except Exception as e:
            await ctx.send(e)
            if isinstance(e, pytweet.Forbidden):
                await ctx.send(f"Posted! check it on https://twitter.com/TweetyBott/status/{tweet.id}")
                await ctx.send(f"Also it return this:\n{e}")

            elif isinstance(e, KeyError):
                await ctx.send("You are not login! use `e!login` command!")

            elif isinstance(e, pytweet.Unauthorized):
                await ctx.send("You have declined your APP Session! Tweety can no longer do action on behalf of you!")

            else:
                raise e

    @commands.command("reply", description="Reply to a tweet, require you to login using `e!login` command!")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def replyTweet(self, ctx: commands.Context, tweet_id: int, *,text):
        error_code = self.bot.set_user_credentials(ctx)
        if error_code == 0:
            await ctx.send("Cannot do interaction, you are not login, Please use `e!login` command to register your account in my database!")
            return
            
        tweet = self.bot.twitter.tweet(text, reply_tweet = tweet_id)
        await ctx.send(f"Posted! check it on https://twitter.com/TweetyBott/status/{tweet.id}")

def setup(bot: commands.Bot):
    bot.add_cog(Twitter(bot))