import discord
from discord.ext import commands
from pytweet import Tweet
from discord.ui import View, Button
from typing import Union
from twitter import TwitterUser

class DisplayModels:
    async def display_tweet(self, tweet: Tweet, user: Union[discord.User, discord.Member, TwitterUser], method, *,ctx = None):
        if not isinstance(tweet, Tweet):
            raise TypeError("Object is not an instance of pytweet.Tweet!")

        try:
            link = tweet.link
        except (TypeError, AttributeError):
            link = f"https://twitter.com/{user.username.replace('@', '', 1)}/status/{str(tweet.id)}"
        
        em=discord.Embed(
            title=f"Posted by {user.name}",
            url=link,
            description=tweet.text,
            color=discord.Color.blue()
        ).set_author(
            name=user.username + f"({user.id})",
            icon_url=user.profile_url,
            url=user.profile_link
        ).set_footer(
            text=f"Conversation ID: {tweet.conversation_id}",
            icon_url=user.profile_url
        ).add_field(
            name="Tweet Date", 
            value=tweet.created_at.strftime('%d/%m/%Y')
        ).add_field(
            name="Source", 
            value=f"[{tweet.source}](https://help.twitter.com/en/using-twitter/how-to-tweet#source-labels)"
        ).add_field(
            name="Reply Setting", 
            value=tweet.raw_reply_setting
        )
        buttons = [Button(label=f"{tweet.like_count} Like Count", emoji="👍", style=discord.ButtonStyle.blurple), Button(label=f"{tweet.retweet_count} Retweet Count", emoji="<:retweet:914877560142299167>", style=discord.ButtonStyle.blurple), Button(label=f"{tweet.reply_count} Reply Count", emoji="🗨️", style=discord.ButtonStyle.blurple)]
        view = View(timeout=200.0)
        for button in buttons:
            view.add_item(button)

        if tweet.media:
            em.set_image(
                url=tweet.media[0].url
            )

        if isinstance(method, discord.Interaction):
            await method.response.send_message(
                content="You know you can do: `e!tweet <tweet_id>` to see other tweet's info!\nlooks like this tweet has a poll, mind checking that out with `e!poll <tweet_id>`?" if tweet.id == 1465231032760684548 and tweet.poll else "You know you can do: `e!tweet <tweet_id>` to see other tweet's info!" if tweet.id == 1465231032760684548 else "looks like this tweet has a poll, mind checking that out with `e!poll <tweet_id>`?" if tweet.poll else "",
                embed=em,
                view=view,
                ephemeral = True
            )

    
        else:
            if tweet.id == 1465231032760684548:
                await method.send("You know you can do: `e!tweet <tweet_id>` to see other tweet's info!")

            if tweet.poll:
                await method.send(
                    "looks like this tweet has a poll, mind checking that out with `e!poll <tweet_id>`?"
                )
                
            await method.send(
                embed=em,
                view=view
            )