import discord
import requests
from discord.ext import commands
from .utils.permissions import bot_join_permissions


class Botevents(commands.Cog):
    """
    This class implements bot's listeners (events)

    Attributes
    ----------
    bot
    join_embed
        Embed that gets posted when bot joins a server
    """

    def __init__(self, bot):
        self.bot = bot
        self.join_embed = discord.Embed(
            title="ReadyRaider bot",
            description="Some info on how to use the bot.",
            colour=discord.Colour.blurple()
        )

    async def add_missing_channels(self):
        """
        Adds comp-channel, raid-channel, loot-channel and botcommands-channel to guild if they are missing
        """
        guild_cog = self.bot.get_cog('Server')

        s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"is_not_empty"}]'
        r = requests.get(self.bot.guildAPI + s)
        guilds = r.json()['response']['results']

        for guild in guilds:
            if 'categoryID' in guild:
                category_id = int(guild['categoryID'])
            else:
                category_id = None
            if 'futurechannelID' in guild:
                future_id = int(guild['futurechannelID'])
            else:
                future_id = None
            if 'pastchannelID' in guild:
                past_id = int(guild['pastchannelID'])
            else:
                past_id = None
            if 'lootchannelID' in guild:
                loot_id = int(guild['lootchannelID'])
            else:
                loot_id = None

            if 'commandsid' in guild:
                commands_id = int(guild['commandsid'])
            else:
                commands_id = None

            await guild_cog.addcategory(int(guild['GuildDiscordID']), category_id, future_id,
                                        past_id, loot_id, commands_id)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event runs when bot is ready. Does bunch of cleaning and setup
        """
        print('Bot is ready.')
        bot_id = self.bot.user.id

        perms = discord.Permissions(permissions=0)
        perms.update(**bot_join_permissions)
        # not totally sure about this,
        # What is this bot_member stuff
        for guild in self.bot.guilds:
            bot_member = guild.get_member(bot_id)
            if bot_member is None:
                continue

            guild_perms = bot_member.guild_permissions

            if guild_perms < perms:
                await guild.leave()
            elif guild.owner.id == bot_id:
                await guild.leave()
        # I'm worried about created infinite channels, doesn't currently check for missing ones
        # await self.add_missing_channels()

    @staticmethod
    def get_join_msg():
        """
        Returns join message embed
        """

        join_message = discord.Embed(
            title="ReadyRaider Bot",
            description='',
            colour=discord.Colour.dark_teal()
        )
        join_message.add_field(name='Useful commands', value="`$set` to SetUp the Bot if it Just Joined`\n"
                                                             "`$help` for general help and list of commands.\n"
                                                             "`$howtouse`\n"
                                                             "`$botinfo` for information on bot.")

        return join_message

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """
        Event triggered when bot joins a guild

        Parameters
        ----------
        guild
            Instance of Guild
        """

        bot_id = self.bot.user.id
        bot_member = guild.get_member(bot_id)

        perms = discord.Permissions(permissions=0)
        perms.update(**bot_join_permissions)

        guild_perms = bot_member.guild_permissions

        # Currently leaves if permissions were denied
        if guild_perms < perms:
            print('Invalid Permissions, Leaving Server')
            await guild.leave()
        else:
            # Do I Want a welcome Message?
            True
            # WHAT HAPPENS WHEN HE JOINS

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """
        Event triggered when bot is removed (leaves) from a guild

        Parameters
        ----------
        guild
            Instance of Guild
        """
        # Should We Remove From DB??, is that a thing we'd want?
        guild_cog = self.bot.get_cog('Server')
        await guild_cog.remove_bot_channels(guild.id)


def setup(bot):
    bot.add_cog(Botevents(bot))
