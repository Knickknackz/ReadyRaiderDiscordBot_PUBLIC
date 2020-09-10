import discord
from discord.ext import commands
from cogs.utils import customcommand


class Misc(commands.Cog):
    """
    contains a few assorted commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 300, commands.BucketType.guild)
    @customcommand.c_command(hidden=True)
    async def botinfo(self, ctx):
        """
        Sends info embed to invokers channel

        Parameters
        ----------
        ctx
            discord context
        """

        info_embed = discord.Embed(
            title="ReadyRaider Bot",
            description="A bot to allows sign-ups for the ReadyRaider system via reactions in Discord.\n You can "
                        "report bugs, ask "
                        "questions about using the bot or request features at the discord server the bot provides.",
            colour=discord.Colour.dark_green()
        )

        info_embed.add_field(name='Links', value="[ReadyRaider](https://readyraider.com)\n"
                                                 "[Discord/Support](https://discord.gg/GByncpz)\n"
                                                 "[Invite Link for the Bot]("
                                                 "https://discord.com/api/oauth2/authorize?client_id"
                                                 "=698180392766930996&permissions=268823792&scope=bot)\n "
                                                 "[Stream Team](https://www.twitch.tv/team/readyraider)\n"
                                                 "[Go Premium](https://www.readyraider.com/premium)")
        # info_embed.set_footer(text="Made by ReadyRaider")

        await ctx.send(embed=info_embed)

    @commands.has_permissions(manage_messages=True)
    @customcommand.c_command(description="Clears given amount of messages from the channel, default = 2.",
                             examples=["clear", "clear 5"],
                             hidden=True)
    async def clear(self, ctx, amount=2):
        """
        Clears messages from text channel

        Parameters
        ----------
        ctx
            discord context
        amount
            how many messages to clear, defaults to 2
        """

        await ctx.channel.purge(limit=amount)

    @commands.cooldown(1, 600, commands.BucketType.guild)
    @commands.has_permissions(administrator=True, manage_guild=True)
    @customcommand.c_command(description="Deletes all ReadyRaider channels, shouldn't be needed.",
                             examples=["delchannels"],
                             hidden=True)
    async def delchannels(self, ctx):
        """
        Deletes all ReadyRaider channels

        Parameters
        ----------
        ctx
            discord context
        """

        guild_cog = self.bot.get_cog('Server')
        await guild_cog.remove_bot_channels(ctx.guild.id)

    @commands.cooldown(1, 300, commands.BucketType.guild)
    @customcommand.c_command(aliases=['howTo', 'howto', 'howToUse'],
                             description="Text Describing How to Use the Bot")
    async def howtouse(self, ctx):
        """
        Sends info about using the bot to invoker's channel

        Parameters
        ----------
        ctx
            discord context
        """
        embed = discord.Embed(title='This section covers the basics on how to use the bot.')
        msg_value = '*upcoming-raids* channel- contains messages that represent the raids created on ReadyRaider.com. '\
                    'It updates every hour, but if you would like them sooner use the "$upcoming" commnad\n\n' \
                    'Sign-Up for raids by reacting with the appropriate emote in the *upcoming-raids* channel. **(' \
                    'Requires a current account on ReadyRaider.com)** \n\n' \
                    'Some commands have cooldowns. This means if you use the command X amount of times in certain ' \
                    'timeframe the cooldown triggers. More info on this with: $help <command>. \n\n' \
                    'Look into topics on bot created channels and enjoy exploring all of the commands!\n' \
                    '\n\n[Dashboard](https://www.readyraider.com/dashboard) - [Support](https://discord.gg/GByncpz) - '\
                    '[Stream Team](https://www.twitch.tv/team/readyraider) - [Go Premium](' \
                    'https://www.readyraider.com/premium) '

        embed.description = msg_value
        await ctx.send(embed=embed)

    @commands.cooldown(5, 300, commands.BucketType.guild)
    @customcommand.c_command(aliases=['bammyx', 'bam', 'miche'],
                             description="Deletes all ReadyRaider channels, shouldn't be needed.",
                             examples=["bamx"],
                             hidden=True)
    async def bamx(self, ctx):
        """
        Blaumeux Meme
        Parameters
        ----------
        ctx
            discord context
        """

        embed = discord.Embed(title='**WOULD YOU LIKE TO CONTACT OUR LORD AND SAVIOR?**',
                              description='REACH OUT TO HIM [HERE](https://www.quiznos.com/menu/classic-sub-sandwich)')
        await ctx.send(embed=embed)

    @commands.cooldown(2, 300, commands.BucketType.guild)
    @customcommand.c_command(aliases=['whatsNew'], description="Displays Recent Updates.")
    async def whatsnew(self, ctx):
        """
        Sends embed about new features to invoker's channel
        Parameters
        ----------
        ctx
            discord context
        """

        embed = discord.Embed(title='8/4/20 Patch:')

        embed.add_field(name='Here are some Recent Updates:',
                        value='Fixed a bug where upcoming raids would stay in the channel way past their start time.\n'
                              'Completed raids channel now updates daily.\n'
                              'Fixed some bugs related to the $set command.\n'
                              'Upcoming raids now includes the order in which raiders sign up.\n'
                              'The loot channel no longer updates daily, but the function "$loot" still works.\n'
                              'Data from NexusHub has been integrated! \nThe following commands are now avaiable:\n'
                              '`$item [itemName]`  \n-Displays information about an item including but not limited to '
                              'droprate and stats.\n\n' 
                              '`$price [itemName]`  \n-Shows auction house data for a given item. \n\n'
                              '`$deals`  \n-Displays currently underpriced(estimated) items on your server/factions '
                              'auction house. \n\n'
                              '`$craftingdeals` \n-Displays recommended crafting items that should yield a big profit '
                              'on your server/factions auction house. '
                        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Misc(bot))
