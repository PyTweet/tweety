from typing import Union, Optional
from discord import User, Member
from .account import Account


class TwitterUser:
    def __init__(self, user: Union[User, Member], account: Optional[Account]):
        self.user = user
        self.twitter_account = account

    @property
    def registered(self) -> bool:
        return str(self.user.id) in list(self.twitter_account.discord_client.db.keys())

    def is_registered(self) -> bool:
        return self.registered
