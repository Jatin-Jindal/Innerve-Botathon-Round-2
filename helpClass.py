import discord
from discord.ext.commands import HelpCommand


class EmbedHelpCommand(HelpCommand):
    COLOUR = discord.Colour(0xff6900)

    def __init__(self, **options):
        options['command_attrs'] = {
            'name': 'Help',
            'brief': 'Shows author and commands',
            'help': 'Get help on any command by using this command followed by the command name\n' +
                    '\tUsage: **{self.clean_prefix} {self.invoked_with} <command>**'
        }

        super().__init__(**options)

    def get_ending_note(self):
        return f'Use {self.clean_prefix} {self.invoked_with} <command> for more info on a command.'

    async def send_bot_help(self, mapping):
        ctx = self.context
        OWNER_ID = 437491079869104138
        owner: discord.User = ctx.bot.get_user(OWNER_ID)
        ownMem = f"<@{OWNER_ID}>" if discord.utils.get(ctx.guild.members, id=OWNER_ID) else "__GhostMander#8725__"

        embed = discord.Embed(
            title='Bot Commands',
            colour=self.COLOUR,
            description=f"Made by {ownMem} for Round 1 of Innerve Bot-a-thon"
        )
        embed.set_author(
            name="Programmed by GhostMander#8725",
            icon_url=owner.avatar_url
        )

        for cog, commands in mapping.items():
            name = '\u200b' if cog is None else cog.qualified_name
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                value = '\n'.join(f"**{c.name: <020}** -\t{c.brief}" for c in commands if not c.hidden)
                if cog and cog.description:
                    value = '{0}\n{1}'.format(cog.description, value)

                embed.add_field(name=name, value=value)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        OWNER_ID = 437491079869104138
        owner: discord.User = ctx.bot.get_user(OWNER_ID)

        embed = discord.Embed(title=command.qualified_name, colour=self.COLOUR)
        embed.set_author(name="GhostMander#8725", icon_url=owner.avatar_url)
        if command.help:
            embed.description = command.help

        embed.set_footer(text=self.get_ending_note())
        if command.hidden and ctx.author.id != OWNER_ID:
            print(f"{ctx.author} tried to get help on hidden command")
            return
        await self.get_destination().send(embed=embed)
