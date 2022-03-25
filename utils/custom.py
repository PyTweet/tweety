from discord.ext.commands import Group, flag, FlagConverter

class CommandGroup(Group):
    def __init__(self, *args, **attrs):
        self.description = attrs.get("description", "No Description Provided")        
        super().__init__(*args, **attrs)

class Options(FlagConverter, case_insensitive=True):
    question: str
    option1: str
    option2: str
    option3: str = flag(default="question")
    option4: str = flag(default="question")