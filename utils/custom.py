from discord.ext.commands import Group

class CommandGroup(Group):
    def __init__(self, *args, **attrs):
        self.description = attrs.get("description", "No Description Provided")        
        super().__init__(*args, **attrs)
        