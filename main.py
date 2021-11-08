import os
import discord
import pytweet
from bot import DisTweetBot
from helpcommand import CustomHelpCommand
from discord.ext import commands
from discord.commands import Option

# pip install git+https://github.com/Pycord-Development/pycord
# pip install git+https://github.com/TheFarGG/PyTweet

twitterbot = pytweet.Client(
    os.environ["bearer_token"],
    consumer_key=os.environ["api_key"],
    consumer_key_secret=os.environ["api_key_secret"],
    access_token=os.environ["access_token"],
    access_token_secret=os.environ["access_token_secret"],
)

bot = DisTweetBot(
    twitterbot,
    command_prefix=commands.when_mentioned_or("e!"),
    help_command=CustomHelpCommand(),
    intents=discord.Intents.all(),
    case_insensitive=True,
    strip_after_prefix=True,
    owner_id=685082846993317953,
    status=discord.Status.idle,
    activity=discord.Game(name="Follow me on twitter at @Genosis101!"),
)

@bot.command(description="Get the bot's ping")
async def ping(ctx):
    await ctx.send(f"PONG! `{round(bot.latency * 1000)}MS`")

@bot.command(description="Get a user info through the user's id or username")
@commands.cooldown(1, 10, commands.BucketType.user)
async def user(ctx, username: str):
    try:
        user=None

        if username.isdigit():
            user=bot.twitter.fetch_user(username)
        
        else:
            user = bot.twitter.fetch_user_by_username(username)
        await ctx.send(
            embed=discord.Embed(
                title=user.name,
                url=user.profile_link,
                description=f":link: {user.link if len(user.link) > 0 else '*This user doesnt provide link*'} | <:compas:879722735377469461> {user.location}\n{user.bio if len(user.bio) > 0 else '*User doesnt provide a bio*'}",
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


@bot.command(description="Get a tweet info through the tweet's id")
@commands.cooldown(1, 10, commands.BucketType.user)
async def tweet(ctx, tweet_id: int):
    try:
        tweet = bot.twitter.fetch_tweet(tweet_id)
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
            text=f"{tweet.created_at.strftime('%Y/%m/%d')} | {tweet.source} | Reply: {tweet.reply_setting}",
            icon_url=user.avatar_url
        ).add_field(
            name="Likes Count 👍", 
            value=tweet.like_count
        ).add_field(
            name="Quotes Count 📰", 
            value=tweet.quote_count
        ).add_field(
            name="Replies Count 🗨️", 
            value=tweet.reply_count
        ).add_field(
            name="Retweetes Count 🗨️", 
            value=tweet.retweet_count
        )
       

        if tweet.embeds:
            em.set_image(
                url=tweet.embeds[0].images[0].url
            )

        await ctx.send(
            embed=em
        )

        if tweet.poll:
            await ctx.send(
                "looks like this tweet has a poll, mind checking that out with `e!poll <tweet_id>`?"
            )

    except pytweet.errors.NotFoundError:
        await ctx.send(f"Could not find user with username(or id): [{tweet_id}].")

@bot.command(description="Get a tweet's poll info through the tweet's id")
@commands.cooldown(1, 10, commands.BucketType.user)
async def poll(ctx, tweet_id: int):
    try:
        tweet = bot.twitter.fetch_tweet(tweet_id)
        user = tweet.author
        if not tweet.poll:
            return await ctx.send("That tweet doesnt have poll")

        em=discord.Embed(
            title=f"Poll for tweet({tweet.id})",
            url=tweet.link,
            description="",
            color=discord.Color.blue()
        ).set_author(
            name=user.username + f"({user.id})",
            icon_url=user.avatar_url,
            url=user.profile_link
        ).set_footer(
            text=f"Duration: {tweet.poll.duration} Seconds | Poll Open: {tweet.poll.voting_status}"
        )

        for option in tweet.poll.options:
            em.description += f"**Option {option.position}**\n. . .**Label:** {option.label}\n. . .**Votes:** {option.votes}\n\n"
        await ctx.send(embed=em)

    except pytweet.errors.NotFoundError:
        await ctx.send("Tweet not found!")

@bot.command(
    description="Follow a user, only an owner of the server can do this command"
)
@commands.is_owner()
@commands.cooldown(1, 10, commands.BucketType.user)
async def follow(ctx, username: str):
    try:
        user = None
        if username.isdigit():
            user = bot.twitter.fetch_user(int(username))

        else:
            user = bot.twitter.fetch_user_by_username(username)

        user.follow()
        await ctx.send(f"{bot.twitter.user.username} Has followed {user.username}!")

    except Exception as error:
        if isinstance(error, pytweet.errors.NotFoundError):
            await ctx.send(f"Could not find user with username(or id): [{username}].")
        else:
            raise error

@bot.command(
    description="UnFollow a user, only an owner of the server can do this command"
)
@commands.is_owner()
@commands.cooldown(1, 10, commands.BucketType.user)
async def unfollow(ctx, username: str):
    try:
        user = None
        if username.isdigit():
            user = bot.twitter.fetch_user(int(username))

        else:
            user = bot.twitter.fetch_user_by_username(username)

        user.unfollow()
        await ctx.send(f"{bot.twitter.user.username} Has unfollowed {user.username}!")

    except Exception as error:
        if isinstance(error, pytweet.errors.NotFoundError):
            await ctx.send(f"Could not find user with username(or id): [{username}].")
            
        else:
            raise error

@bot.command(
    description="Return users that i followed"
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def following(ctx):
    users=bot.twitter.user.following
    txt=""
    for num, user in enumerate(users):
        txt += f"{num + 1}. {user.username}({user.id})\n"
    
    await ctx.send(f"Here are **{len(users)}** cool people i followed!\n{txt}")

@bot.command(
    description="Send a message to a user!"
)
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.is_owner()
async def send(ctx, user_id:str, *,text: str):
    user=None
    if user_id.isdigit():
        user=bot.twitter.fetch_user(user_id)
    else:
        user=bot.twitter.fetch_user_by_username(user_id)

    try:
        user.send(text)
    except pytweet.errors.Forbidden:
        await ctx.send("cannot send message to that user!")
    else:
        await ctx.send(f"Send message to {user.username}")

#Slash Commands
@bot.slash_command(description="Say hello to me")
async def hello(ctx, name: Option(str, "The name that you want to greet")):
    name = name or ctx.author.name
    await ctx.respond(f"Hello {name}!")


os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_RETAIN'] = 'True'
os.environ['JISHAKU_FORCE_PAGINATOR'] = 'True'

token = os.environ["token"]
bot.run(token)
