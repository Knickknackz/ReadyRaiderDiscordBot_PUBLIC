from discord.ext import commands
from .utils.permissions import default_role_perms_comp_raid, bot_perms, default_role_perms_commands
from .utils import checks
from .utils import customcommand
import requests
from .utils.globalfunctions import search_format
import discord
from datetime import datetime
from urllib.parse import quote
import asyncio


class Guild(commands.Cog, name='Server'):
    """
    Includes some commands that are useful if user deletes bot made channels or guild is somehow not stored in db.
    """

    def __init__(self, bot):
        self.bot = bot

    async def addlootchannel(self, guild, category):
        """
        Adds loot-channel (text-channel) to guild under category

        Parameters
        ----------
        guild
            Instance of Guild
        category
            The Category to add the channel to
        """
        topic = "This channel displays information about loot received."

        overwrites_raids_comps = {guild.default_role: default_role_perms_comp_raid,
                                  self.bot.user: bot_perms}
        # \U00002694 CROSSED SWORDS
        loot_channel = await guild.create_text_channel('\U00002694 Loot', category=category,
                                                       overwrites=overwrites_raids_comps, topic=topic)
        return loot_channel.id

    async def addfuturechannel(self, guild, category):
        """
        Adds future-raids-channel (text-channel) to guild under category

        Parameters
        ----------
        guild
            Instance of Guild
        category
            Category to add the channel to
        """

        topic = "This channel displays all upcoming raids in the next week."

        overwrites_raids_comps = {guild.default_role: default_role_perms_comp_raid,
                                  self.bot.user: bot_perms}
        # \U0001F5D3 CALENDAR
        future_channel = await guild.create_text_channel('\U0001F5D3 Upcoming Raids', category=category,
                                                         overwrites=overwrites_raids_comps, topic=topic)
        return future_channel.id

    async def addpastchannel(self, guild, category):
        """
          Adds commands-channel (text-channel) to guild under cateogry

            Parameters
          ----------
         api
          guild
              Instance of Guild
        category
        """

        topic = "This channel displays all completed raids in the last week."
        overwrites_raids_comps = {guild.default_role: default_role_perms_comp_raid,
                                  self.bot.user: bot_perms}
        # \U00002611 BALLOT BOX WITH CHECK
        past_channel = await guild.create_text_channel('\U00002611 Completed Raids', category=category,
                                                       overwrites=overwrites_raids_comps, topic=topic)
        return past_channel.id

    @staticmethod
    async def addcommandschannel(guild, category):
        """
        Adds commands-channel (text-channel) to guild under cateogry

        Parameters
        ----------
        guild
            Instance of Guild
        category
            Category To add the channel to
        """
        topic_bc = "You can use bot-commands here or any other channel. If you already have a channel for " \
                   "this purpose or don't want to use this channel, feel free to delete it."
        overwrites_bot_commands = {guild.default_role: default_role_perms_commands,
                                   guild.me: bot_perms}
        # \U0001F5E3 Shouting Head
        cmd_channel = await guild.create_text_channel('\U0001F5E3 RR-commands', overwrites=overwrites_bot_commands,
                                                      category=category, topic=topic_bc)
        return cmd_channel.id

    async def addcategory(self, guild_id, category_id, future_channel_id, past_channel_id,
                          loot_channel_id, commands_channel_id):
        """
        Adds category to guild and creates channels if needed. Also moves these channels under
        category if they already aren't

        Parameters
        ----------
        guild_id
            Instance of Guild
        category_id
        future_channel_id
        past_channel_id
        loot_channel_id
        commands_channel_id
            Ids for the Channels/Category
        """
        updateDB = False
        guild = self.bot.get_guild(guild_id)

        if not guild:
            return

        # Check if channel exists in db and not guild
        if category_id is not None:
            category = guild.get_channel(int(category_id))
            if category is None:
                updateDB = True
                category = await guild.create_category('\U0001F432 ReadyRaider Bot')

        # Category not in DB, create new one and a cmd-channel \U0001F
        # 432 = DRAGON
        else:
            updateDB = True
            category = await guild.create_category('\U0001F432 ReadyRaider Bot')

        # Check if channel exists in db and not guild
        if future_channel_id is not None:
            future_channel = guild.get_channel(int(future_channel_id))
            if future_channel is None:
                updateDB = True
                future_channel_id = await self.addfuturechannel(guild, category)
            else:
                True
                # await future_channel.edit(category=category) No longer forces the use of the category
        else:
            updateDB = True
            future_channel_id = await self.addfuturechannel(guild, category)

        # Check if channel exists in db and not guild
        if loot_channel_id is not None:
            loot_channel = guild.get_channel(int(loot_channel_id))
            if loot_channel is None:
                updateDB = True
                loot_channel_id = await self.addlootchannel(guild, category)
            else:
                True
                # await loot_channel.edit(category=category) No longer forces the use of the category
        else:
            updateDB = True
            loot_channel_id = await self.addlootchannel(guild, category)

        # Check if channel exists in db and not guild
        if past_channel_id is not None:
            past_channel = guild.get_channel(int(past_channel_id))
            if past_channel is None:
                updateDB = True
                past_channel_id = await self.addpastchannel(guild, category)
            else:
                True
                # await past_channel.edit(category=category)
        else:
            updateDB = True
            past_channel_id = await self.addpastchannel(guild, category)

        # Check if channel exists in db and not guild
        if commands_channel_id is not None:
            commands_channel = guild.get_channel(int(commands_channel_id))
            if commands_channel is None:
                updateDB = True
                commands_channel_id = await self.addcommandschannel(guild, category)
            else:
                True
                # await commands_channel.edit(category=category)
        else:
            updateDB = True
            commands_channel_id = await self.addcommandschannel(guild, category)

        if updateDB:
            api_cog = self.bot.get_cog('RR_API')
            guildData = await api_cog.guild_data(guild.id)
            rr_id = guildData['_id']
            body = {"guild": rr_id,
                    "pastchannelid": str(past_channel_id),
                    "futurechannelid": str(future_channel_id),
                    "lootchannelid": str(loot_channel_id),
                    "commandsid": str(commands_channel_id),
                    "categoryid": str(category.id)
                    }
            headers = {"Authorization": "Bearer " + self.bot.api_key}
            r = requests.post(self.bot.channelAPI, data=body, headers=headers)

    async def remove_bot_channels(self, guild_id):
        """
        Runs addcategory for guild
        Parameters
        ----------
        guild_id
            Instance of guild
        """
        api_cog = self.bot.get_cog('RR_API')
        channelInfo = await api_cog.get_channel_info(guild_id)

        if not channelInfo:
            print("Server Name Not in DB, Can't delete channels. Server: " + str(guild_id))
            return
        if channelInfo['futurechannelid']:
            await self.bot.get_channel(int(channelInfo['futurechannelid'])).delete()
        if channelInfo['pastchannelid']:
            await self.bot.get_channel(int(channelInfo['pastchannelid'])).delete()
        if channelInfo['lootchannelid']:
            await self.bot.get_channel(int(channelInfo['lootchannelid'])).delete()
        if channelInfo['commandschannelid']:
            await self.bot.get_channel(int(channelInfo['commandschannelid'])).delete()
        if channelInfo['categoryid']:
            await self.bot.get_channel(int(channelInfo['categoryid'])).delete()

    async def add_bot_channels(self, guild):
        """
        Runs addcategory for guild
        Parameters
        ----------
        guild
            Instance of guild
        """
        api_cog = self.bot.get_cog('RR_API')
        channelInfo = await api_cog.get_channel_info(guild.id)
        if not channelInfo:
            print("Server Name Not in DB, Can't add channels. Server: " + str(guild.id))
            return
        category_id = channelInfo['categoryid']
        future_id = channelInfo['futurechannelid']
        past_id = channelInfo['pastchannelid']
        loot_id = channelInfo['lootchannelid']
        commands_id = channelInfo['commandschannelid']

        await self.addcategory(guild.id, category_id, future_id, past_id, loot_id, commands_id)

    @commands.cooldown(2, 600, commands.BucketType.guild)
    @checks.has_any_permission(administrator=True, manage_guild=True)
    @customcommand.c_command(description="Re-adds bot made channels in case deleted.",
                             perms=['Administrator', "manage server"],
                             hidden=True)
    async def fixchannels(self, ctx):
        """
        Runs add_bot_channels manually

        Parameters
        ----------
        ctx
        """

        await self.add_bot_channels(ctx.guild)

    @commands.cooldown(3, 600, commands.BucketType.guild)
    @checks.has_any_permission(administrator=True, manage_guild=True)
    @customcommand.c_command(aliases=['Set'],
                             description="Used to set the bot up. Requires a ReadyRaider Guild as well and the "
                                         "Discord account of this command to have his Discord Linked.",
                             perms=['Administrator', "manage server"],
                             examples=["set"],
                             hidden=True)
    async def set(self, ctx):
        """

        Parameters
        ----------
        ctx
        """
        discord_name = ctx.author.name
        discord_suffix = ctx.author.discriminator
        discord_full = quote(discord_name + ' #' + discord_suffix)

        s = search_format('DiscordID', 'equals', discord_full)
        s = "".join(str(s).split())
        r = requests.get(self.bot.discordAPI + '?constraints=[' + s + ']')
        userData = r.json()['response']['results']

        s = '?constraints=[{"key":"GuildDiscordID","constraint_type":"equals","value":"' + str(ctx.guild.id) + '"}]'
        r = requests.get(self.bot.guildAPI + s)
        guild = r.json()['response']['results']

        if guild:
            await ctx.send('Error! This Server is Already Signed up on ReadyRaider')
            return

        if userData:
            unique_id = userData[0]['_id']
        else:
            # DMs User to update RR account
            dmchannel = await ctx.author.create_dm()
            await dmchannel.send(
                "Error! Please Link Your Discord Account to ReadyRaider Here: https://www.readyraider.com/profile2")
            return

        headers = {"Authorization": "Bearer " + self.bot.api_key}
        body = {"id": str(unique_id), "serverid": str(ctx.guild.id)}
        requests.post(self.bot.initAPI, data=body, headers=headers)

        if r.status_code == 200:
            await asyncio.sleep(3.0)

            api_cog = self.bot.get_cog('RR_API')
            guildInfo = await api_cog.guild_data(ctx.guild.id)

            if not guildInfo:
                print("Server Name Not in DB, Can't add channels. Server: " + str(ctx.guild.name) + '/' + str(
                    ctx.guild.id))
                embed = discord.Embed(
                    title='Error!',
                    description='The Discord Bot Failed to Link to ReadyRaider.com',
                    colour=discord.Colour.from_rgb(255, 0, 00),
                    timestamp=datetime.utcnow()
                )
                await ctx.send(embed=embed)
                return
            else:
                embed = discord.Embed(
                    title='Success!',
                    description='You have successfully set-up your ReadyRaider Discord Bot!',
                    colour=discord.Colour.from_rgb(50, 205, 50),
                )

                embed.set_thumbnail(url='https://img.icons8.com/fluent/96/000000/check-all.png')
                await ctx.send(embed=embed)

                misc_cog = self.bot.get_cog('Misc')

                await ctx.invoke(misc_cog.howtouse)

                await self.addcategory(ctx.guild.id, None, None, None, None, None)


        else:
            embed = discord.Embed(
                title='Error!',
                description='The Discord Bot Failed to Link to ReadyRaider.com',
                colour=discord.Colour.from_rgb(255, 0, 00),
                timestamp=datetime.utcnow()
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Guild(bot))
