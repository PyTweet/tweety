import discord
import pytweet
import asyncio
from discord.ext import commands
from typing import Union
from utils.views import Paginator
from utils.custom import CommandGroup
from objects import to_dict

class Twitter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        "login",
        description="Create a set of user access token so you can use twitter related commands in with your account!",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def login(self, ctx: commands.Context):
        oauth = self.bot.twitter.http.oauth_session
        raw_data = await (await self.bot.db_cursor.execute("SELECT * FROM main WHERE discord_user_id = ?", (ctx.author.id,))).fetchone()
        data = to_dict(raw_data, token=..., token_secret=..., screen_name=..., discord_user_id=..., user_id=...,)
        oauth_url = oauth.create_oauth_url("direct_messages")
        
        if data:
            try:
                await ctx.send(
                    f"You are were already logged in as: `{data['screen_name']}` with id `{data['user_id']}`"
                )
                return
            except KeyError:
                user = await self.bot.get_twitter_user(ctx.author.id, ctx)
                if not user:
                    return
    
                await ctx.send(
                    f"You are were already logged in as: `{user.twitter_account.username}` with id `{user.twitter_account.id}`"
                )
                return
        em = discord.Embed(
            title="Steps",
            description="Follow my instruction to register your account to my database! You have exactly **5 minutes** to this, you can always retry the command if you did not make it!",
            color = discord.Color.blue()
        ).add_field(
            name="Step 1",
            value="I will send a url to your dm in exactly 10 seconds from now, click it."
        ).add_field(
            name="Step 2",
            value="after that you have to authorize TweetyBott application."
        ).add_field(
            name="Step 3",
            value="Then you will get redirected to https://twitter.com/, the url contains an oauth token & verifier. Copy the full url and send it to my dm! The url should look like this: https://twitter.com/home?oauth_token=xxxxxxxxxxxxxxxxxxxxx&oauth_verifier=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            inline=False
        ).add_field(
            name="Get Stuck?",
            value="Join the official [discord server](https://discord.gg/XHBhg6A4jJ) to get some help!",
            inline=False
        ).set_footer(
            text="Do not show your oauth token and verifier!"
        )
        
        await ctx.send("Check your dm!")
        await ctx.author.send(embed=em)
        await asyncio.sleep(10)
        await ctx.author.send(embed=discord.Embed(
            description=f"Authorize TweetyBott Application in this **[URL]({oauth_url})** after that refer to the 2nd step!",
            color=discord.Color.blue()
        ))
        
        msg = await self.bot.wait_for("message", timeout=60 * 5, check=lambda msg: msg.guild is None and msg.author.id != self.bot.user.id)
        await ctx.author.send(
            f"Got the url ||`{msg.content}`|| ! please wait for couple of seconds!"
        )

        try:
            domain, url = msg.content.split("?")
            raw_oauth_token, raw_oauth_verifier = url.split("&")
            oauth_token_credential, oauth_token = raw_oauth_token.split("=")
            oauth_verifier_credential, oauth_verifier = raw_oauth_verifier.split("=")
            oauth_token, oauth_token_secret, user_id, screen_name = oauth.post_oauth_token(
                oauth_token, oauth_verifier
            )
    
            oauth_token_credential, oauth_token = oauth_token.split("=")
            oauth_verifier_credential, oauth_secret = oauth_token_secret.split("=")
            user_id_credential, user_id = user_id.split("=")
            screen_name_credential, screen_name = screen_name.split("=")
        except (TypeError, ValueError):
            await ctx.author.send("Wrong url sent! use `e!login` command again and make sure you put the right url next time!")
            return
            
        await self.bot.db_cursor.execute("INSERT INTO main (token, token_secret, screen_name, discord_user_id, user_id) VALUES (?, ?, ?, ?, ?)", (oauth_token, oauth_secret, screen_name, ctx.author.id, int(user_id)))
        await self.bot.db.commit()
        em = discord.Embed(
          title="Authorized :white_check_mark:",
          description=f"You have authorized the application and succesfully logged in as **`{screen_name}`**! You can now use twitter related commands, use  `e!help` command to see which commands you can use! \n\nYou can starts with posting a tweet from discord to twitter through post command: `e!post - just setting up my twttr`\n\nIf you want to decline the connection between the application and your account, you could always go to [settings](https://twitter.com/settings) -> [apps_and_sessions](https://twitter.com/settings/apps_and_sessions) -> [connected apps](https://twitter.com/settings/connected_apps) and revoke TweetyBott access, keep in mind that you have to use `e!login` if you want to use twitter related commands again after you successfully revoked access.",
          color=discord.Color.blue()
        )
        await ctx.author.send(f"Back to {ctx.channel.mention}!")
        await ctx.send(embed=em)

    @commands.command(
        "logout",
        description="Logout from your current twitter account, means the data in my database will get deleted and will be invalid! This command requires you to login using `e!login` command!",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def logout(self, ctx: commands.Context):
        user = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not user:
            return

        yes = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        no = discord.ui.Button(label="NO", style=discord.ButtonStyle.red)

        async def yes_callback(interaction):
            no.disabled = True
            yes.disabled = True
            await self.bot.db_cursor.execute("DELETE FROM main WHERE discord_user_id = ?", (ctx.author.id,))
            await self.bot.db.commit()
            await ctx.send(
                "Logged out! If you want to use twitter commands again, you can use `e!login`"
            )

        async def no_callback(interaction):
            no.disabled = True
            yes.disabled = True
            await interaction.response.edit_message("Exit command!")
            await msg.edit(view=view)
            return

        yes.callback = yes_callback
        no.callback = no_callback
        view = discord.ui.View()
        view.add_item(yes)
        view.add_item(no)

        msg = await ctx.send("Are you sure you want to logout?", view=view)

    @commands.command(
        "user",
        description="A command for user lookup, This command requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def user_lookup(self, ctx: commands.Context, username: Union[str, int] = None):
        author = (await self.bot.get_twitter_user(ctx.author.id, ctx)).twitter_account
        client = author.client

        if not username:
            await self.client_lookup(ctx)
            return

        if username.isdigit():
            user = client.fetch_user(username)

        else:
            user = client.fetch_user_by_username(username)

        if not user:
            await ctx.send(
                f"Could not find user with username (or id): [{username}]."
            )
            return

        await self.bot.displayer.display_user(ctx, user, author)

    @commands.command(
        "tweet",
        description="A command for a tweet lookup, This command requires you to login using the `e!login` command!",
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def tweet_lookup(
        self, ctx: commands.Context, tweet_id: str = "1465231032760684548"
    ):
        try:
            tweet_id = int(tweet_id)
        except ValueError:
            await ctx.send(
                "Please send a tweet ID after typing the command! Example: `e!tweet 1465231032760684548`"
            )
            return

        client = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not client:
            return

        tweet = client.twitter_account.client.fetch_tweet(tweet_id)
        if not tweet:
            await ctx.send("That tweet ID does not exist!")
            return

        await self.bot.displayer.display_tweet(ctx, tweet, None)

    @commands.command(
        "poll",
        description="Lookup a poll in twitter! This command requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def poll_lookup(self, ctx, tweet_id):
        client = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not client:
            return

        try:
            tweet_id = int(tweet_id)
        except (ValueError, TypeError):
            await ctx.send("Wrong arguments passed!")
        else:
            tweet = client.twitter_account.client.fetch_tweet(tweet_id)
            user = tweet.author
            if not tweet:
                await ctx.send("Tweet not found.")
                return

            if not tweet.poll:
                return await ctx.send("The tweet doesn't have poll.")
                return

            em = (
                discord.Embed(
                    title=f"Poll for tweet({tweet.id})",
                    url=tweet.url,
                    description="",
                    color=discord.Color.blue(),
                )
                .set_author(
                    name=user.username + f"({user.id})",
                    icon_url=user.profile_image_url,
                    url=user.profile_image_url,
                )
                .set_footer(
                    text=f"Duration: {tweet.poll.duration} Seconds | Poll Open: {tweet.poll.voting_status}"
                )
            )

            for option in tweet.poll.options:
                em.description += f"**Option {option.position}**\n. . . **Label:** {option.label}\n. . . **Votes:** {option.votes}\n\n"
            await ctx.send(embed=em)

    @commands.command(
        "account",
        aliases=["profile", "acc"],
        description="See your account! This command requires you to login using `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def client_lookup(self, ctx):
        me = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not me:
            return

        id = me.twitter_account.user_id
        if not id:
            id = me.twitter_account.id
            self.bot.db[str(ctx.author.id)][
                "user_id"
            ] = id  # Store the id in the database if it was not in the database, this is use to avoid ratelimit!
        
        await self.bot.displayer.display_user(ctx, me.twitter_account, me.twitter_account)

    @commands.command(
        "following",
        aliases=["followings"],
        description="Returns users that you followed, This command requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def following_lookup(self, ctx: commands.Context):
        client = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not client:
            return

        paginator = commands.Paginator(prefix="", suffix="", max_size=370)
        user = client.twitter_account
        try:
            users = user.fetch_following().content
            if not users:
                await ctx.send(f"You have 0 following!")
                return

            for num, following in enumerate(users):
                paginator.add_line(f"{num + 1}. {following.username}({following.id})")

        except TypeError:
            await ctx.send(f"You have 0 following!")
            return

        else:
            em = discord.Embed(
                title=f"Total of {len(users)} users!",
                description="",
                color=discord.Color.blue(),
            ).set_author(
                name=f"Viewing {user.username}'s following", icon_url=user.profile_image_url
            )
            em.description = paginator.pages[0]
            paginator = Paginator(paginator, ctx.author, embed=em)
            await ctx.send(embed=em, view=paginator)

    @commands.command(
        "follower",
        aliases=["followers"],
        description="Return users that you followed, This command requires you to login using `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def follower_lookup(self, ctx: commands.Context):
        client = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not client:
            return

        paginator = commands.Paginator(prefix="", suffix="", max_size=370)
        user = client.twitter_account
        try:
            users = user.fetch_following().content
            if not users:
                await ctx.send(f"You have 0 followers!")
                return

            for num, following in enumerate(users):
                paginator.add_line(f"{num + 1}. {following.username}({following.id})")

        except TypeError:
            await ctx.send(f"You have 0 followers!")
            return

        else:
            em = discord.Embed(
                title=f"Total of {len(users)} users!",
                description="",
                color=discord.Color.blue(),
            ).set_author(
                name=f"Viewing {user.username}'s followers", icon_url=user.profile_image_url
            )
            em.description = paginator.pages[0]
            paginator = Paginator(paginator, ctx.author, embed=em)
            await ctx.send(embed=em, view=paginator)

    @commands.command(
        "follow",
        description="Follow a user, require you to login using `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def follow_user(self, ctx: commands.Context, username: str):
        client = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not client:
            return

        user = None
        me = client.twitter_account
        if username.isdigit():
            user = client.twitter_account.client.fetch_user(int(username))

        else:
            user = client.twitter_account.client.fetch_user_by_username(username)

        if not user:
            await ctx.send("User does not exist!")
            return

        user.follow()
        await ctx.send(f"{me.username} Has followed {user.username}!")

    @commands.command(
        "unfollow",
        description="UnFollow a user, require you to login using `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unfollow_user(self, ctx: commands.Context, username: str):
        client = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not client:
            return

        user = None
        me = client.twitter_account
        if username.isdigit():
            user = client.twitter_account.client.fetch_user(int(username))

        else:
            user = client.twitter_account.client.fetch_user_by_username(username)

        if not user:
            await ctx.send("Username/id is not exist!")
            return

        user.unfollow()
        await ctx.send(f"{me.username} Has unfollowed {user.username}!")

    @commands.command(
        "send",
        description="Sends a message to a user, requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def send_message_to_user(
        self, ctx: commands.Context, username: Union[str, int], *, text: str
    ):
        user = None
        client = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not client:
            return

        if username.isdigit():
            user = client.twitter_account.client.fetch_user(int(username))

        else:
            user = client.twitter_account.client.fetch_user_by_username(username)

        if not user:
            await ctx.send("User does not exist!!")
            return

        user.send(text)
        await ctx.send(f"Send message to {user.username}")

    @commands.group(
        cls=CommandGroup,
        invoke_without_command=True,
        case_insensitive=True,
        description="A group of commands use for interaction between a twitter user and a tweet!"
    )
    async def post(self, ctx: commands.Context, *, text=None):
        tweet = None
        user = await self.bot.get_twitter_user(ctx.author.id, ctx)
        
        if not user:
            return

        try:
            tweet = user.twitter_account.client.tweet(text)
            await ctx.send(f"Posted! Check it on {tweet.url}")
        except Exception as e:
            if isinstance(e, pytweet.Forbidden):
                await ctx.send(f"Posted! check it on {tweet.url}")
                await ctx.send(f"Also it return this:\n{e}")

            elif isinstance(e, KeyError):
                await ctx.send("You are not login! use `e!login` command!")

            elif isinstance(e, AttributeError):
                await ctx.send(f"Could not find tweet with id: [{id}].")

            elif isinstance(e, pytweet.Unauthorized):
                await ctx.send(
                    "You have declined your APP Session! Tweety can no longer do action on behalf of you!"
                )
                raise e

            else:
                raise e

    @post.command(
        "-reply",
        description="Reply to a tweet, requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reply_tweet(self, ctx: commands.Context, tweet_id: int, *, text):
        user = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not user:
            return

        tweet = user.twitter_account.client.tweet(text, reply_tweet=tweet_id)
        await ctx.send(
            f"Posted! check it on {tweet.url}"
        )

    @post.command(
        "-quote",
        description="Quote a tweet, requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def quote_tweet(self, ctx: commands.Context, tweet_id: int, *, text):
        user = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not user:
            return

        tweet = user.twitter_account.client.tweet(text, reply_tweet=tweet_id)
        await ctx.send(f"Posted! check it on {tweet.url}")

    @post.command(
        "-retweet",
        description="Reply to a tweet, requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def retweet_tweet(self, ctx: commands.Context, tweet_id: int):
        user = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not user:
            return

        tweet = user.twitter_account.client.fetch_tweet(tweet_id)
        tweet.retweet()
        await ctx.send(
            f"Posted! check it on {tweet.url}"
        )

    @post.command(
        "-like",
        description="Like a tweet, requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def like_tweet(self, ctx: commands.Context, tweet_id: int):
        user = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not user:
            return

        tweet = user.twitter_account.client.fetch_tweet(tweet_id)
        tweet.like()
        await ctx.send(
            f"Liked the tweet!"
        )

    @post.command(
        "-unlike",
        description="Unlike a tweet, requires you to login using the `e!login` command!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def unlike_tweet(self, ctx: commands.Context, tweet_id: int):
        user = await self.bot.get_twitter_user(ctx.author.id, ctx)
        if not user:
            return

        tweet = user.twitter_account.client.fetch_tweet(tweet_id)
        tweet.unlike()
        await ctx.send(
            f"Unliked the tweet!"
        )


def setup(bot: commands.Bot):
    bot.add_cog(Twitter(bot))
