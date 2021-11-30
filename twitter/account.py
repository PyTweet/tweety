from typing import Optional, Union, Dict
from discord import Client
from discord.ext.commands import Bot

from pytweet import Client as TwitterClient
from pytweet import User as TwitterUser

class Account(TwitterUser):
    def __init__(self, discord_client: Union[Client, Bot], twitter_client: Optional[TwitterClient], twitter_credentials: Dict):
        self.discord_client = discord_client
        self.client = twitter_client
        self.__twitter_credentials = twitter_credentials
        self.set_credentials() 
        super().__init__(self.user.original_payload, self.client.http)

    def set_credentials(self):
        self.client.http.access_token = self.access_token
        self.client.http.access_token_secret = self.access_token_secret

    @property
    def access_token(self):
        return self.__twitter_credentials.get("token", None)

    @property
    def access_token_secret(self):
        return self.__twitter_credentials.get("token_secret", None)

    @property
    def screen_name(self):
        try:
            return self.__twitter_credentials.get("screen_name", None).replace("@", "")
        except Exception:
            return self.__twitter_credentials.get("screen_name", None)

    @property
    def user_id(self):
        try:
            return int(self.__twitter_credentials.get("user_id", None))
        except (ValueError, TypeError):
            return self.__twitter_credentials.get("user_id", None)

    @property
    def screen_name_mention(self):
        return self.__twitter_credentials.get("screen_name", None)

    @property
    def user(self):
        return self.client.account

    account = user #Alias for user property.