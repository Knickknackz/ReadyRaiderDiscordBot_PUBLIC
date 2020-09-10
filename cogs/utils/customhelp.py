import discord
from discord.ext import commands


class CustomHelpCommand(commands.DefaultHelpCommand):
    """
    A subclass of DefaultHelpCommand for custom implementation

    Attributes
    ----------
    mod_cmds
        List of mod commands that require specific discord permissions or mod role
    prefixes
        List of prefixes that the bot recognizes
    """

    def __init__(self, **kwargs):
        super().__init__(verify_checks=False, command_attrs={"hidden": True})
        self.mod_cmds = kwargs.pop('mod_cmds')
        self.prefixes = ", ".join(kwargs.pop('prefixes'))

    async def send_command_help(self, command):
        """
        Sends help embed of given command to invokers channel
        Parameters
        ----------
        command
            Instance of Command
        """

        # Fixes help command subclassing issue with custom command
        if command.name == 'help':
            return

        embed = discord.Embed(
            title='Command: ' + command.name,
            colour=discord.Colour.gold()
        )

        cd = getattr(command._buckets._cooldown, 'per', None)

        if cd is not None:
            cd = int(cd)
            if cd < 60:
                cd_value = str(cd) + ' second(s)'
            else:
                cd_value = str(cd // 60) + ' minute(s)'
        else:
            cd_value = '-'

        if command.description:
            desc = command.description
        else:
            desc = "-"

        if command.examples is not None:
            example = "\n".join(('$' + x for x in command.examples))
        else:
            example = '-'

        if command.perms is not None:
            perms = "\n".join(perm for perm in command.perms)
        else:
            perms = '-'

        if command.aliases:
            aliases = "\n".join(command.aliases)
        else:
            aliases = "-"

        if command.signature:
            usage_value = '$' + command.name + ' ' + command.signature + '\n [] parameters are required unless a ' \
                                                                         'default value is shown.\n '
        else:
            usage_value = '$' + command.name

        embed.description = desc
        embed.add_field(name='Aliases', value=aliases, inline=True)
        embed.add_field(name='Permissions (Any)', value=perms, inline=True)
        embed.add_field(name='Cooldown', value=cd_value, inline=True)
        embed.add_field(name="Example(s)", value=example, inline=True)
        embed.add_field(name='Formatting', value=usage_value, inline=True)
        embed.add_field(name="\u200b",
                        value="You may be able to use the command multiple times before triggering the cooldown.\n" \
                              "You should get a response or see the results of your command." +
                              '\n[Dashboard](https://www.readyraider.com/dashboard) - [Support]('
                              'https://discord.gg/GByncpz) - ' +
                              '[Stream Team](https://www.twitch.tv/team/readyraider) - [Go Premium]('
                              'https://www.readyraider.com/premium)',
                        inline=False)

        dest = self.get_destination()

        await dest.send(embed=embed)

    async def send_cog_help(self, cog):
        """
        Sends help embed of given cog to invokers channel

        Parameters
        ----------
        cog
            Instance of Cog
        """

        # Not relevant to user
        if cog.qualified_name in ('Admin', 'Background', 'Botevents', 'CommandErrorHandler'):
            return

        embed = discord.Embed(
            title=f"Category: {cog.qualified_name}",
            description=cog.description or "-",
            colour=discord.Colour.gold()
        )

        sorted_commands = await self.filter_commands(cog.get_commands(), sort=True)

        embed.add_field(name='Commands:', value='\n'.join(str(cmd) + ' - $' + cmd.name + " " + cmd.signature for
                                                          cmd in sorted_commands))
        embed.add_field(name="\u200b",
                        value="""[] parameters are optional.\nIf you want to give a parameter with spaces use
                        quotation marks " " """ +
                              '\n[Dashboard](https://www.readyraider.com/dashboard) - [Support](https://discord.gg/GByncpz) - ' +
                              '[Stream Team](https://www.twitch.tv/team/readyraider) - [Go Premium](https://www.readyraider.com/premium)',
                        inline=False)

        dest = self.get_destination()

        await dest.send(embed=embed)

    async def send_bot_help(self, mapping):
        """
        Sends embed with a list of all commands and other info to invokers channel
        Parameters
        ----------
        mapping
            Dict with Cogs and their Commands
        """
        embed = discord.Embed(
            title="All Commands",
            description="To get information on a specific command or category type: " \
                        "`$help <command name>`",
            colour=discord.Colour.gold()
        )

        no_category = "No category:"
        for cog, cog_commands in mapping.items():
            sorted_commands = await self.filter_commands(cog_commands)
            if sorted_commands:
                name = cog.qualified_name if cog is not None else no_category
                cmd_name = '\u200b\n__**' + name + '**__\n'
                for cmd in sorted_commands:
                    if cmd.signature:
                        cmd_name += '$' + str(cmd) + ' ' + cmd.signature
                    else:
                        cmd_name += '$' + str(cmd)

                    if cmd.description:
                        desc = ('' + cmd.description)
                    else:
                        desc = ('No Description')
                    embed.add_field(name=cmd_name, value=desc, inline=False)
                    cmd_name = ''

        embed.add_field(name="\u200b",
                        value="""[] parameters are optional.\nIf you want to give a parameter with spaces use
                        quotation marks " " """ +
                              '\n[Dashboard](https://www.readyraider.com/dashboard) - [Support](https://discord.gg/GByncpz) - ' +
                              '[Stream Team](https://www.twitch.tv/team/readyraider) - [Go Premium](https://www.readyraider.com/premium)',
                        inline=False)

        dest = self.get_destination()

        await dest.send(embed=embed)
